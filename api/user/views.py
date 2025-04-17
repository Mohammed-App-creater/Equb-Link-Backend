from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404
import random

from user.permissions import (
    IsAdminUser,
    IsCustomerUser,
    IsCustomerOrIsAdminUser,
    IsEqubAdminUser,
)

from .models import Customer, Admin, EqubAdmin
from .serializers import UserSerializer, CustomerDataSerializer, AdminSerializer, EqubAdminDataSerializer

User = get_user_model()

@api_view(["POST"])
def signup(request):
    try:
        data = request.data
        email = data["email"].lower()
        password = data["password"]
        re_password = data["re_password"]
        role = data["role"]

        if password != re_password:
            return Response({"message": "error", "error": "Passwords do not match."},
                            status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8:
            return Response({"message": "error", "error": "Password must be at least 8 characters."},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"message": "error", "error": "User with this email already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create user based on role
        if role == "admin":
            user = User.objects.create_admin(email=email, password=password)
        elif role == "customer":
            user = User.objects.create_customer(email=email, password=password)
        elif role == "equb_admin":
            user = User.objects.create_equb_admin(email=email, password=password)
        else:
            return Response({"message": "error", "error": "Undefined Role"},
                            status=status.HTTP_400_BAD_REQUEST)

        token = Token.objects.create(user=user)
        serializer = UserSerializer(instance=user)

        name = data.get("name")
        phone = data.get("phone")
        photo = request.FILES.get("photo")  # optional

        if role == "customer":
            referred_by = data.get("referred_by")
            referral_code = (name[:4] if len(name) > 4 else name) + str(random.randint(1111, 9999))
            Customer.objects.create(
                user=user,
                name=name,
                phone=phone,
                photo=photo,
                referral_code=referral_code,
                referred_by=referred_by,
            )
        elif role == "equb_admin":
            EqubAdmin.objects.create(user=user, name=name, phone=phone, photo=photo)
        elif role == "admin":
            Admin.objects.create(user=user, name=name, phone=phone, photo=photo)

        return Response({
            "message": "success",
            "token": token.key,
            "data": serializer.data,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("Signup Error:", e)
        return Response({"message": "error", "error": "Something went wrong during registration."},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def login(request):
    email = request.data.get("email").lower()
    password = request.data.get("password")

    user = get_object_or_404(User, email=email)

    if not user.check_password(password):
        return Response({"message": "error", "error": "Wrong details"},
                        status=status.HTTP_400_BAD_REQUEST)

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    if user.is_admin:
        profile = Admin.objects.filter(user=user).first()
        serializer = AdminSerializer(instance=profile)
    elif user.is_customer:
        profile = Customer.objects.filter(user=user).first()
        serializer = CustomerDataSerializer(instance=profile)
    elif user.is_equb_admin:
        profile = EqubAdmin.objects.filter(user=user).first()
        serializer = EqubAdminDataSerializer(instance=profile)
    else:
        serializer = UserSerializer(instance=user)

    return Response({
        "message": "success",
        "token": token.key,
        "data": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def test_token(request):
    return Response({"message": f"success for {request.user.email}"})


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def adminGetAll(request):
    if request.method == "GET":
        admins = Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
