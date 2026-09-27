"""
Protected media serving.

Everything under MEDIA_ROOT used to be public. Now:
  - receipt_images/*  -> only the payer, the equb owner, a platform admin,
                         or anyone holding a short-lived signed URL
                         (serializers emit those for receipt_image).
  - everything else   -> public (category/advert images, profile photos,
                         which the apps load without an auth header).

In production the web server must NOT serve /media/receipt_images/ itself,
or this check is bypassed. Serve it through Django (or X-Sendfile).
"""
import posixpath
from pathlib import Path

from django.conf import settings
from django.core import signing
from django.http import FileResponse, Http404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Payment

RECEIPT_PREFIX = "receipt_images/"
SIGNED_URL_MAX_AGE = 60 * 60 * 24  # 24h
_signer_salt = "equb.media"


def signed_media_url(request, file_field):
    """Absolute URL to a protected file with a signature the media view accepts."""
    if not file_field:
        return None
    name = file_field.name
    sig = signing.dumps(name, salt=_signer_salt)
    url = f"{settings.MEDIA_URL}{name}?sig={sig}"
    return request.build_absolute_uri(url) if request is not None else url


def _user_may_view_receipt(user, name):
    if not user or not user.is_authenticated:
        return False
    if user.is_admin or user.is_superuser:
        return True
    return Payment.objects.filter(receipt_image=name).filter(
        models_q_payer_or_owner(user)
    ).exists()


def models_q_payer_or_owner(user):
    from django.db.models import Q
    return Q(equb_member__user=user) | Q(equb_member__equb__owner=user)


@api_view(["GET"])
@permission_classes([AllowAny])
def serve_media(request, path):
    # Normalise and refuse path traversal
    name = posixpath.normpath(path).lstrip("/")
    if name.startswith("..") or "/../" in f"/{name}/":
        raise Http404
    full = Path(settings.MEDIA_ROOT) / name
    if not full.is_file():
        raise Http404

    if name.startswith(RECEIPT_PREFIX):
        sig = request.GET.get("sig")
        allowed = False
        if sig:
            try:
                allowed = signing.loads(sig, salt=_signer_salt, max_age=SIGNED_URL_MAX_AGE) == name
            except signing.BadSignature:
                allowed = False
        if not allowed:
            allowed = _user_may_view_receipt(request.user, name)
        if not allowed:
            return Response({"error": "Not authorized to view this file."}, status=403)

    response = FileResponse(open(full, "rb"))
    # Never let a stored file execute as a page on this origin
    response["X-Content-Type-Options"] = "nosniff"
    response["Content-Disposition"] = f'inline; filename="{full.name}"'
    response["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return response
