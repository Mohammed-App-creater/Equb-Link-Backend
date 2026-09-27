"""
Upload helpers shared by every view that accepts a user file.

- validate_image_upload(): allow-listed extensions, size cap, and a real
  image check via Pillow (a .jpg that is actually HTML is rejected). Django
  model FileField/ImageField do NOT run this on .create(), so views must
  call it explicitly.
- random_upload_path(): replaces the client-supplied filename with a UUID so
  files cannot be guessed or overwrite each other.
"""
import os
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_UPLOAD_MB = getattr(settings, "MAX_UPLOAD_MB", 5)


def validate_image_upload(uploaded_file, max_mb: int = MAX_UPLOAD_MB):
    """Raise django ValidationError if the upload is not an acceptable image."""
    if uploaded_file is None:
        return None
    ext = os.path.splitext(uploaded_file.name or "")[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Only JPG, PNG or WEBP images are allowed.")
    if uploaded_file.size > max_mb * 1024 * 1024:
        raise ValidationError(f"Image must be smaller than {max_mb} MB.")
    try:
        img = Image.open(uploaded_file)
        img.verify()
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError("The file is not a valid image.")
    finally:
        uploaded_file.seek(0)
    return uploaded_file


def _random_path(folder):
    def upload_to(instance, filename):
        ext = os.path.splitext(filename or "")[1].lower() or ".jpg"
        return f"{folder}/{uuid.uuid4().hex}{ext}"
    return upload_to


# Named functions (not lambdas) so migrations can serialize them.
def receipt_upload_path(instance, filename):
    return _random_path("receipt_images")(instance, filename)


def profile_upload_path(instance, filename):
    return _random_path("uploads/profile")(instance, filename)
