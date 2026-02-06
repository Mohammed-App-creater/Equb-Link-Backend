from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

from .models import Customer, EqubAdmin, Admin


class UserSerializer(serializers.ModelSerializer):
    class Meta(object):
        model = User
        fields = "__all__"


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
    name = serializers.CharField(max_length=30, required=False)
    phone = serializers.CharField(max_length=15, required=False)
    email = serializers.EmailField(required=False)

    def validate_phone(self, value):
        if User.objects.exclude(id=self.context["request"].user.id).filter(phone=value).exists():
            raise serializers.ValidationError("Phone number already in use.")
        return value

    def update(self, user, validated_data):
        # Update user fields
        user.phone = validated_data.get("phone", user.phone)
        user.email = validated_data.get("email", user.email)
        user.save()

        # Update profile name (based on role)
        profile = None
        if hasattr(user, "admin"):
            profile = user.admin
        elif hasattr(user, "customer"):
            profile = user.customer
        elif hasattr(user, "equbadmin"):
            profile = user.equbadmin

        if profile and "name" in validated_data:
            profile.name = validated_data["name"]
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
        return attrs