from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Customer, EqubAdmin, Admin
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from equbApp.uploads import validate_image_upload


class UserSerializer(serializers.ModelSerializer):
    """Account fields safe to expose. Never the password hash, permissions or staff flags."""
    class Meta(object):
        model = User
        fields = [
            "id", "phone", "email",
            "is_customer", "is_equb_admin", "is_admin",
            "is_active", "date_joined", "last_login",
        ]
        read_only_fields = fields


class AdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = Admin
        fields = "__all__"


class AdminPostSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )

    class Meta(object):
        model = Admin
        fields = "__all__"




class CustomerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )


    class Meta(object):
        model = Customer
        fields = "__all__"


class CustomerDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = Customer
        fields = "__all__"


class EqubAdminSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=User.objects.all()
    )


    class Meta(object):
        model = EqubAdmin
        fields = "__all__"


class EqubAdminDataSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta(object):
        model = EqubAdmin
        fields = "__all__"




class ProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    photo = serializers.ImageField(required=False, validators=[validate_image_upload])

    def validate_email(self, value):
        user = self.context["request"].user
        if User.objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError("Email already in use.")
        return value

    def update(self, user, validated_data):
        # Update email
        if "email" in validated_data:
            user.email = validated_data["email"]
            user.save()

        # Resolve profile based on role
        profile = None
        if hasattr(user, "admin"):
            profile = user.admin
        elif hasattr(user, "customer"):
            profile = user.customer
        elif hasattr(user, "equbadmin"):
            profile = user.equbadmin

        # Update photo
        if profile and "photo" in validated_data:
            profile.photo = validated_data["photo"]
            profile.save()

        return user


# =========================
# CHANGE PASSWORD SERIALIZER
# =========================

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        try:
            validate_password(attrs["new_password"])
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"new_password": exc.messages})
        return attrs