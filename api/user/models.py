from django.db import models
import uuid
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import RegexValidator


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
        user = self.create_user(phone, password, email)
        user.is_equb_admin = True
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
    photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)

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
    photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)

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
    photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)

    def __str__(self):
        return self.name


# from django.db import models
# import uuid
# from django.contrib.auth.models import (
#     AbstractBaseUser,
#     BaseUserManager,
#     PermissionsMixin,
# )
# from django.core.validators import RegexValidator


# class MyAccountManager(BaseUserManager):
#     def create_user(self, email, password=None):
#         if not email:
#             raise ValueError("Users must have an email address")

#         user = self.model(
#             email=self.normalize_email(email).lower(),
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_admin(self, email, password=None):
#         user = self.create_user(email=email, password=password)
#         user.is_admin = True
#         user.save(using=self._db)
#         return user

#     def create_customer(self, email, password=None):
#         user = self.create_user(email=email, password=password)
#         user.is_customer = True
#         user.save(using=self._db)
#         return user

#     def create_equb_admin(self, email, password=None):
#         user = self.create_user(email=email, password=password)
#         user.is_equb_admin = True
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None):
#         user = self.create_user(email=email, password=password)
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


# class Account(AbstractBaseUser, PermissionsMixin):
#     email = models.EmailField(max_length=60, unique=True)
#     date_joined = models.DateTimeField(auto_now_add=True)
#     last_login = models.DateTimeField(auto_now=True)
#     is_active = models.BooleanField(default=True)

#     # User roles
#     is_admin = models.BooleanField(default=False)
#     is_customer = models.BooleanField(default=False)
#     is_equb_admin = models.BooleanField(default=False)

#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)

#     USERNAME_FIELD = "email"
#     objects = MyAccountManager()

#     def __str__(self):
#         return self.email


# User = Account


# class Admin(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=30)
#     phone = models.CharField(
#         validators=[RegexValidator(
#             regex=r"^\+?1?\d{9,15}$",
#             message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
#         )],
#         max_length=17,
#         blank=True,
#     )
#     photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name


# class Customer(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=30)
#     phone = models.CharField(
#         validators=[RegexValidator(
#             regex=r"^(09|07|2519|2517)\d{8}$",
#             message="Phone number must be valid Ethiopian format.",
#         )],
#         max_length=17,
#         blank=True,
#     )
#     photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     referral_code = models.CharField(max_length=8, null=True, blank=True)
#     referred_by = models.CharField(max_length=8, null=True, blank=True)
#     referral_point = models.FloatField(default=0,null=True,blank=True)


#     def __str__(self):
#         return self.name


# class EqubAdmin(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=30)
#     phone = models.CharField(
#         validators=[RegexValidator(
#             regex=r"^(09|07|2519|2517)\d{8}$",
#             message="Phone number must be valid Ethiopian format.",
#         )],
#         max_length=17,
#         blank=True,
#     )
#     photo = models.FileField(upload_to="uploads/profile", null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)


#     def __str__(self):
#         return self.name
