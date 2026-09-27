from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
from .models import Customer, Admin, EqubAdmin
from .serializers import (
    UserSerializer,
    CustomerDataSerializer,
    AdminSerializer,
    EqubAdminDataSerializer,
    AdminPostSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
)
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsAdminUser
from .throttles import (
    LoginThrottle,
    PasswordResetConfirmThrottle,
    PasswordResetRequestThrottle,
    SignupThrottle,
)
from .authentication import issue_token
from rest_framework.decorators import throttle_classes
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from equbApp.uploads import validate_image_upload
from rest_framework.response import Response
User = get_user_model()


# =========================
# SIGNUP
# =========================
@api_view(["POST"])
@throttle_classes([SignupThrottle])
def signup(request):
    data = request.data

    phone = data.get("phone")
    email = data.get("email")  # OPTIONAL
    password = data.get("password")
    re_password = data.get("re_password")
    role = data.get("role")
    name = data.get("name")
    photo = request.FILES.get("photo")

    if not all([phone, password, re_password, role, name]):
        return Response(
            {"error": "Missing required fields"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if password != re_password:
        return Response({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(phone=phone).exists():
        return Response(
            {"error": "Phone number already registered"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Self-registration is customer-only. Admin and owner accounts are created
    # by a platform admin (api/admin/create/, equb-admin/create/).
    if role != "customer":
        return Response(
            {"error": "Self-registration is only available for customers."},
            status=status.HTTP_403_FORBIDDEN,
        )
    try:
        validate_password(password)
        validate_image_upload(photo)
    except DjangoValidationError as exc:
        return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_customer(phone, password, email)
    token = issue_token(user)

    # Create profile
    if role == "customer":
        referral_code = name[:4] + str(random.randint(1000, 9999))
        profile = Customer.objects.create(
            user=user,
            name=name,
            phone=phone,
            photo=photo,
            referral_code=referral_code,
        )
        serializer = CustomerDataSerializer(profile)

    elif role == "admin":
        profile = Admin.objects.create(
            user=user,
            name=name,
            phone=phone,
            photo=photo,
        )
        serializer = AdminPostSerializer(profile)

    else:
        profile = EqubAdmin.objects.create(
            user=user,
            name=name,
            phone=phone,
            photo=photo,
        )
        serializer = EqubAdminDataSerializer(profile)

    return Response(
        {
            "message": "success",
            "token": token.key,
            "data": serializer.data,
        },
        status=status.HTTP_201_CREATED,
    )

# =========================
# CUSTOMER SIGNUP
# =========================
@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([SignupThrottle])
def customer_signup(request):
    data = request.data

    phone = data.get("phone")
    email = data.get("email")
    password = data.get("password")
    re_password = data.get("re_password")
    name = data.get("name")
    photo = request.FILES.get("photo")

    if not all([phone, password, re_password, name]):
        return Response({"error": "Missing fields"}, status=400)

    if password != re_password:
        return Response({"error": "Passwords do not match"}, status=400)

    if User.objects.filter(phone=phone).exists():
        return Response({"error": "Phone already exists"}, status=400)

    try:
        validate_password(password)
        validate_image_upload(photo)
    except DjangoValidationError as exc:
        return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_customer(phone, password, email)
    token = issue_token(user)

    referral_code = name[:4].upper() + str(random.randint(1000, 9999))

    customer = Customer.objects.create(
        user=user,
        name=name,
        phone=phone,
        photo=photo,
        referral_code=referral_code,
    )

    return Response({
        "message": "success",
        "role": "customer",
        "token": token.key,
        "data": CustomerDataSerializer(customer).data
    }, status=201)

# =========================
# CREATE ADMIN (BY SUPERADMIN)      
# =========================

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_admin(request):
    data = request.data

    phone = data.get("phone")
    password = data.get("password")
    name = data.get("name")

    if not all([phone, password, name]):
        return Response({"error": "phone, password and name are required."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(phone=phone).exists():
        return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(password)
    except DjangoValidationError as exc:
        return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_admin(phone, password)

    admin = Admin.objects.create(
        user=user,
        name=name,
        phone=phone,
    )

    return Response({
        "message": "admin created",
        "data": AdminPostSerializer(admin).data
    }, status=201)

# =========================
# CREATE EQUB ADMIN (BY SUPERADMIN) 

@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def create_equb_admin(request):
    data = request.data

    phone = data.get("phone")
    password = data.get("password")
    name = data.get("name")

    if not all([phone, password, name]):
        return Response({"error": "phone, password and name are required."}, status=status.HTTP_400_BAD_REQUEST)
    if User.objects.filter(phone=phone).exists():
        return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(password)
    except DjangoValidationError as exc:
        return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_equb_admin(phone, password)

    equb_admin = EqubAdmin.objects.create(
        user=user,
        name=name,
        phone=phone,
    )

    return Response({
        "message": "equb admin created",
        "data": EqubAdminDataSerializer(equb_admin).data
    }, status=201)


# =========================
# LOGIN (PHONE BASED) 
# =========================
@api_view(["POST"])
@throttle_classes([LoginThrottle])
def login(request):
    phone = request.data.get("phone")
    password = request.data.get("password")

    if not phone or not password:
        return Response(
            {"error": "Phone and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(phone=phone).first()

    # Same message and status whether the phone exists or not (no enumeration).
    if not user or not user.check_password(password) or not user.is_active:
        return Response(
            {"error": "Invalid phone number or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = issue_token(user)

    if user.is_customer:
        serializer = CustomerDataSerializer(Customer.objects.get(user=user))
    elif user.is_admin:
        serializer = AdminSerializer(Admin.objects.get(user=user))
    elif user.is_equb_admin:
        serializer = EqubAdminDataSerializer(EqubAdmin.objects.get(user=user))
    else:
        serializer = UserSerializer(user)

    return Response(
        {
            "message": "success",
            "access_token": token.key,
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
    
# =========================
# LOGIN (PHONE BASED) with token
# =========================
@api_view(["POST"])
@throttle_classes([LoginThrottle])
def loginWithToken(request):
    phone = request.data.get("phone")
    password = request.data.get("password")

    if not phone or not password:
        return Response(
            {"error": "Phone and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(phone=phone).first()

    # Same message and status whether the phone exists or not (no enumeration).
    if not user or not user.check_password(password) or not user.is_active:
        return Response(
            {"error": "Invalid phone number or password."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token = issue_token(user)

    if user.is_customer:
        serializer = CustomerDataSerializer(Customer.objects.get(user=user))
    elif user.is_admin:
        serializer = AdminSerializer(Admin.objects.get(user=user))
    elif user.is_equb_admin:
        serializer = EqubAdminDataSerializer(EqubAdmin.objects.get(user=user))
    else:
        serializer = UserSerializer(user)

    return Response(
        {
            "message": "success",
            "token": token.key,
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# =========================
# # UPDATE PROFILE (CUSTOMER, ADMIN, EQUB ADMIN)
# ==========================

class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ProfileUpdateSerializer(
            instance=request.user,
            data=request.data,
            context={"request": request},
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Profile updated successfully"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "Incorrect Old password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
        
        
# =========================
# GET CURRENT USER PROFILE
# =========================


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user

    # Fall back to the bare account when the profile row is missing
    # (e.g. accounts created from the shell) instead of a 500.
    serializer = None
    if user.is_customer:
        profile = Customer.objects.filter(user=user).first()
        if profile:
            serializer = CustomerDataSerializer(profile)
    elif user.is_admin:
        profile = Admin.objects.filter(user=user).first()
        if profile:
            serializer = AdminSerializer(profile)
    elif user.is_equb_admin:
        profile = EqubAdmin.objects.filter(user=user).first()
        if profile:
            serializer = EqubAdminDataSerializer(profile)
    if serializer is None:
        serializer = UserSerializer(user)

    return Response(
        {
            "message": "success",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )


# =========================== Logout ===========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    """Revokes the caller's token server-side. Clients discard it locally too."""
    if request.auth is not None:
        request.auth.delete()
    return Response({"detail": "Logged out."})


# =========================== Owner panel profile ===========================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def owner_profile(request):
    """
    Flat profile for the owner admin panel: account flags plus the display
    name / photo from the EqubAdmin (or Admin) profile row.
    """
    user = request.user
    if not (user.is_equb_admin or user.is_admin):
        return Response(
            {"error": "Owner account required."},
            status=status.HTTP_403_FORBIDDEN,
        )

    profile = None
    if user.is_equb_admin:
        profile = EqubAdmin.objects.filter(user=user).first()
    if profile is None and user.is_admin:
        profile = Admin.objects.filter(user=user).first()

    photo = None
    photo_field = getattr(profile, "photo", None)
    if photo_field:
        photo = request.build_absolute_uri(photo_field.url)

    return Response({
        "id": user.id,
        "phone": user.phone,
        "email": user.email,
        "is_admin": user.is_admin,
        "is_equb_admin": user.is_equb_admin,
        "is_customer": user.is_customer,
        "name": getattr(profile, "name", None),
        "photo": photo,
    })


# =========================== Password reset (phone OTP) ===========================
import hashlib
import hmac
import secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.decorators import authentication_classes

from .models import PasswordResetCode
from .sms import SmsDeliveryError, send_sms

RESET_CODE_MAX_ATTEMPTS = 5
RESET_RESEND_COOLDOWN = timedelta(seconds=60)
RESET_GENERIC_RESPONSE = {
    "detail": "If an account exists for that phone number, a reset code has been sent by SMS."
}


def _phone_candidates(raw):
    """Accept 0911..., 911..., 251911... or +251911... and match the stored form."""
    cleaned = "".join(ch for ch in str(raw or "") if ch.isdigit() or ch == "+")
    if not cleaned:
        return []
    candidates = {cleaned}
    digits = cleaned.lstrip("+")
    if digits.startswith("251") and len(digits) == 12:
        local = digits[3:]
        candidates.update({"+" + digits, digits, "0" + local, local})
    elif digits.startswith("0") and len(digits) == 10:
        local = digits[1:]
        candidates.update({"+251" + local, "251" + local, local})
    elif len(digits) == 9:
        candidates.update({"+251" + digits, "251" + digits, "0" + digits})
    return list(candidates)


def _find_user_by_phone(raw):
    candidates = _phone_candidates(raw)
    if not candidates:
        return None
    return User.objects.filter(phone__in=candidates, is_active=True).first()


def _hash_reset_code(code):
    return hmac.new(settings.SECRET_KEY.encode(), code.encode(), hashlib.sha256).hexdigest()


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetRequestThrottle])
def password_reset_request(request):
    """
    Body: {"phone": "..."}. Sends a 6-digit code by SMS. The response is the
    same whether or not the phone exists (no account enumeration). A new code
    is not sent within 60s of the previous one; the previous one stays valid.
    """
    phone = request.data.get("phone")
    if not phone:
        return Response({"error": "phone is required."}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.DEBUG and settings.SMS_PROVIDER == "console":
        # No real SMS provider configured: never print codes to production logs.
        return Response(
            {"error": "Password reset by SMS is not available yet. Please contact support."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    user = _find_user_by_phone(phone)
    if user is None:
        return Response(RESET_GENERIC_RESPONSE)

    now = timezone.now()
    latest = user.password_reset_codes.filter(used_at__isnull=True, expires_at__gt=now).first()
    if latest and now - latest.created_at < RESET_RESEND_COOLDOWN:
        return Response(RESET_GENERIC_RESPONSE)

    # Only one live code per user
    user.password_reset_codes.filter(used_at__isnull=True).update(used_at=now)

    code = f"{secrets.randbelow(10 ** 6):06d}"
    ttl = settings.PASSWORD_RESET_CODE_TTL_MINUTES
    PasswordResetCode.objects.create(
        user=user,
        code_hash=_hash_reset_code(code),
        expires_at=now + timedelta(minutes=ttl),
    )

    try:
        send_sms(
            user.phone,
            f"Your Equb Link password reset code is {code}. It expires in {ttl} minutes.",
        )
    except SmsDeliveryError as exc:
        # Same generic reply as for unknown numbers, so an SMS outage cannot be
        # used to tell which phones have accounts. The failure is logged.
        import logging
        logging.getLogger(__name__).warning("Password reset SMS failed for user %s: %s", user.pk, exc)
        return Response(RESET_GENERIC_RESPONSE)

    payload = dict(RESET_GENERIC_RESPONSE)
    if settings.DEBUG and settings.SMS_PROVIDER == "console":
        # Development convenience: no SMS is actually sent with the console provider.
        payload["debug_code"] = code
    return Response(payload)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
@throttle_classes([PasswordResetConfirmThrottle])
def password_reset_confirm(request):
    """
    Body: {"phone", "code", "new_password", "confirm_password"}.
    On success the password is changed and every existing auth token for the
    account is revoked, so the user signs in again everywhere.
    """
    phone = request.data.get("phone")
    code = str(request.data.get("code") or "").strip()
    new_password = request.data.get("new_password") or ""
    confirm_password = request.data.get("confirm_password") or ""

    if not all([phone, code, new_password, confirm_password]):
        return Response(
            {"error": "phone, code, new_password and confirm_password are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if new_password != confirm_password:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        validate_password(new_password)
    except DjangoValidationError as exc:
        return Response({"error": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    invalid = Response(
        {"error": "Invalid or expired code. Please request a new one."},
        status=status.HTTP_400_BAD_REQUEST,
    )

    user = _find_user_by_phone(phone)
    if user is None:
        return invalid

    now = timezone.now()
    entry = user.password_reset_codes.filter(used_at__isnull=True).first()
    if entry is None or entry.expires_at < now:
        return invalid
    if entry.attempts >= RESET_CODE_MAX_ATTEMPTS:
        return Response(
            {"error": "Too many incorrect attempts. Please request a new code."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if not hmac.compare_digest(entry.code_hash, _hash_reset_code(code)):
        entry.attempts += 1
        entry.save(update_fields=["attempts"])
        remaining = RESET_CODE_MAX_ATTEMPTS - entry.attempts
        return Response(
            {"error": "Invalid code.", "remaining_attempts": remaining},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user.set_password(new_password)
    user.save()
    entry.used_at = now
    entry.save(update_fields=["used_at"])
    Token.objects.filter(user=user).delete()

    return Response({"detail": "Password reset successfully. Please sign in with your new password."})
