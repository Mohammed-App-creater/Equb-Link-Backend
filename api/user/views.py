from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from rest_framework.authtoken.models import Token
from django.shortcuts import get_object_or_404

from django.db.models import Q



from .models import Customer, EqubAdmin, Admin
from datetime import datetime


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from user.permissions import (
    IsAdminUser,
    IsCustomerUser,
    IsCustomerOrIsAdminUser,
    IsEqubAdminUser,
)



import math, random

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token
import random

from django.contrib.auth import get_user_model
from user.models import Customer, EqubAdmin, Admin
from user.serializers import UserSerializer

User = get_user_model()


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.core.validators import RegexValidator
import random
import uuid

from user.models import User
from .models import Customer, Admin, EqubAdmin
from .serializers import UserSerializer, CustomerDataSerializer, AdminSerializer, EqubAdminDataSerializer


@api_view(["POST"])
def signup(request):
    try:
        data = request.data

        email = data["email"].lower()
        password = data["password"]
        re_password = data["re_password"]
        role = data["role"]

        if password != re_password:
            return Response(
                {"message": "error", "error": "Passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(password) < 8:
            return Response(
                {"message": "error", "error": "Password must be at least 8 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"message": "error", "error": "User with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user account
        if role == "admin":
            User.objects.create_admin(email=email, password=password)
        elif role == "customer":
            User.objects.create_customer(email=email, password=password)
        elif role == "equb_admin":
            User.objects.create_equb_admin(email=email, password=password)
        else:
            return Response(
                {"message": "error", "error": "Undefined Role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.get(email=email)
        serializer = UserSerializer(instance=user)
        token = Token.objects.create(user=user)

        name = data.get("name")
        phone = data.get("phone")
        photo = request.FILES.get("photo")  # Optional profile image

        if role == "customer":
            referred_by = data.get("referred_by")
            referral_code = (name[:4] if len(name) > 4 else name) + str(random.randint(1111, 9999))

            Customer.objects.create(
                user=user,
                name=name,
                phone=phone,
                photo=photo,
                referral_code=referral_code,
                referred_by=referred_by
            )

        elif role == "equb_admin":
            EqubAdmin.objects.create(user=user, name=name, phone=phone)

        elif role == "admin":
            Admin.objects.create(user=user, name=name, phone=phone)

        return Response(
            {
                "message": "success",
                "token": token.key,
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        print("Signup Error:", e)
        return Response(
            {"message": "error", "error": "Something went wrong while registering."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def login(request):
    user = get_object_or_404(User, email=request.data["email"].lower())

    if not user.check_password(request.data["password"]):
        return Response(
            {"message": "error", "error": "Wrong Details"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

    # Default serializer
    serializer = UserSerializer(instance=user)

    if user.is_admin:
        admin_obj = Admin.objects.filter(user=user).first()
        serializer = AdminSerializer(instance=admin_obj)
    elif user.is_customer:
        customer_obj = Customer.objects.filter(user=user).first()
        serializer = CustomerDataSerializer(instance=customer_obj)
    elif user.is_equb_admin:
        equb_admin_obj = EqubAdmin.objects.filter(user=user).first()
        serializer = EqubAdminDataSerializer(instance=equb_admin_obj)

    return Response(
        {"message": "success", "token": token.key, "data": serializer.data},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def test_token(request):
    return Response({"message": "success for {}".format(request.user.email)})




@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated, IsAdminUser])
def adminGetAll(request):
    if request.method == "GET":
        user = Admin.objects.all()
        userSer = AdminSerializer(user, many=True)
        return Response(userSer.data, status=status.HTTP_200_OK)


