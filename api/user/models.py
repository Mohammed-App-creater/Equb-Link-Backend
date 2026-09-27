from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator
from equbApp.uploads import profile_upload_path


# =========================
# USER MANAGER
# =========================
class MyAccountManager(BaseUserManager):

    def create_user(self, phone, password=None, email=None):
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(phone=phone, email=email)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_customer(self, phone, password=None, email=None):
        user = self.create_user(phone, password, email)
        user.is_customer = True
        user.save()
        return user

    def create_admin(self, phone, password=None, email=None):
        user = self.create_user(phone, password, email)
        user.is_admin = True
        user.is_staff = True
        user.save()
        return user

    def create_equb_admin(self, phone, password=None, email=None):
        if not phone:
            raise ValueError("Phone number is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(
            phone=phone,
            email=email,
            is_equb_admin=True,
            # Owners use the owner panel, not the Django admin site.
            is_staff=False,
            is_active=True,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password, email=None):
        user = self.create_user(phone, password, email)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


# =========================
# USER MODEL
# =========================
class Account(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^(09|07|2519|2517)\d{8}$",
                message="Phone number must be valid Ethiopian format",
            )
        ],
    )
    email = models.EmailField(max_length=60, blank=True, null=True)

    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    # roles
    is_admin = models.BooleanField(default=False)
    is_customer = models.BooleanField(default=False)
    is_equb_admin = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    objects = MyAccountManager()

    def __str__(self):
        return self.phone


User = Account


# =========================
# ADMIN PROFILE
# =========================
class Admin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to=profile_upload_path, null=True, blank=True)

    def __str__(self):
        return self.name


# =========================
# CUSTOMER PROFILE
# =========================
class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to=profile_upload_path, null=True, blank=True)

    referral_code = models.CharField(max_length=8, null=True, blank=True)
    referred_by = models.CharField(max_length=8, null=True, blank=True)
    referral_point = models.FloatField(default=0)

    def __str__(self):
        return self.name


# =========================
# EQUB ADMIN PROFILE
# =========================
class EqubAdmin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    photo = models.ImageField(upload_to=profile_upload_path, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Make sure user is marked as EqubAdmin
        if self.user and not self.user.is_equb_admin:
            self.user.is_equb_admin = True
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# =========================
# PASSWORD RESET CODE (phone OTP)
# =========================
class PasswordResetCode(models.Model):
    """One-time 6-digit code sent by SMS. Only the HMAC of the code is stored."""

    user = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="password_reset_codes"
    )
    code_hash = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.PositiveSmallIntegerField(default=0)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        state = "used" if self.used_at else "active"
        return f"Reset code for {self.user.phone} ({state})"
