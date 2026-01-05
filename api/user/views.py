from django.contrib.auth import get_user_model
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
)
import random

User = get_user_model()


# =========================
# SIGNUP
# =========================
@api_view(["POST"])
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

    # Create user
    if role == "customer":
        user = User.objects.create_customer(phone, password, email)
    elif role == "admin":
        user = User.objects.create_admin(phone, password, email)
    elif role == "equb_admin":
        user = User.objects.create_equb_admin(phone, password, email)
    else:
        return Response({"error": "Invalid role"}, status=400)

    token = Token.objects.create(user=user)

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
# LOGIN (PHONE BASED)
# =========================
@api_view(["POST"])
def login(request):
    phone = request.data.get("phone")
    password = request.data.get("password")

    if not phone or not password:
        return Response(
            {"error": "Phone and password required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User.objects.filter(phone=phone).first()

    if not user:
        return Response(
            {"error": "Phone number not registered"},
            status=status.HTTP_404_NOT_FOUND,
        )

    if not user.check_password(password):
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    Token.objects.filter(user=user).delete()
    token = Token.objects.create(user=user)

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


# from django.contrib.auth import get_user_model
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# import random
# from django.contrib.auth import authenticate
# from django.shortcuts import get_object_or_404
# from rest_framework.authtoken.models import Token
# from django.core.validators import RegexValidator

# from .models import Customer, Admin, EqubAdmin
# from .serializers import (
#     UserSerializer,
#     CustomerDataSerializer,
#     AdminSerializer,
#     EqubAdminDataSerializer,AdminPostSerializer
# )

# User = get_user_model()

# @api_view(["POST"])
# def signup(request):
#     try:
#         data = request.data
#         email = data.get("email", "").lower()
#         password = data.get("password")
#         re_password = data.get("re_password")
#         role = data.get("role")
#         name = data.get("name")
#         phone = data.get("phone")
#         photo = request.FILES.get("photo")  # Optional file

#         if not all([phone, password, re_password, role, name]):
#             return Response({"message": "error", "error": "Missing required fields."}, status=status.HTTP_400_BAD_REQUEST)

#         if password != re_password:
#             return Response({"message": "error", "error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

#         if len(password) < 8:
#             return Response({"message": "error", "error": "Password must be at least 8 characters."}, status=status.HTTP_400_BAD_REQUEST)

#         if User.objects.filter(phone=phone).exists():
#             return Response({"message": "error", "error": "phone already in use."}, status=status.HTTP_400_BAD_REQUEST)

#         # Create user based on role
#         if role == "admin":
#             user = User.objects.create_admin(phone=phone, password=password)
#         elif role == "customer":
#             user = User.objects.create_customer(phone=phone, password=password)
#         elif role == "equb_admin":
#             user = User.objects.create_equb_admin(phone=phone, password=password)
#         else:
#             return Response({"message": "error", "error": "Invalid role provided."}, status=status.HTTP_400_BAD_REQUEST)

#         token = Token.objects.create(user=user)

#         # Save role-specific profile
#         if role == "customer":
#             referred_by = data.get("referred_by")
#             referral_code = (name[:4] if len(name) >= 4 else name) + str(random.randint(1000, 9999))
#             profile = Customer.objects.create(
#                 user=user,
#                 name=name,
#                 phone=phone,
#                 photo=photo,
#                 referral_code=referral_code,
#                 referred_by=referred_by
#             )
#             serializer = CustomerDataSerializer(profile)
#         elif role == "admin":
#             profile = Admin.objects.create(
#                 user=user,
#                 name=name,
#                 phone=phone,
#                 photo=photo
#             )
#             serializer = AdminPostSerializer(profile)
#         elif role == "equb_admin":
#             profile = EqubAdmin.objects.create(
#                 user=user,
#                 name=name,
#                 phone=phone,
#                 photo=photo
#             )
#             serializer = EqubAdminDataSerializer(profile)

#         return Response({
#             "message": "success",
#             "token": token.key,
#             "data": serializer.data
#         }, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         print("Signup error:", e)
#         return Response({"message": "error", "error": "Something went wrong."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.authtoken.models import Token
# from django.shortcuts import get_object_or_404
# from .models import User, Admin, Customer, EqubAdmin
# from .serializers import AdminSerializer, CustomerDataSerializer, EqubAdminDataSerializer, UserSerializer

# @api_view(["POST"])
# def login(request):
#     user = get_object_or_404(User, phone=request.data["phone"].lower())

#     if not user.check_password(request.data["password"]):
#         return Response(
#             {"message": "error", "error": "Wrong Details"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     Token.objects.filter(user=user).delete()
#     token = Token.objects.create(user=user)

#     # Default serializer
#     serializer = UserSerializer(instance=user)

#     if user.is_admin:
#         admin_obj = Admin.objects.filter(user=user).first()
#         serializer = AdminSerializer(instance=admin_obj)
#     elif user.is_customer:
#         customer_obj = Customer.objects.filter(user=user).first()
#         serializer = CustomerDataSerializer(instance=customer_obj)
#     elif user.is_equb_admin:
#         equb_admin_obj = EqubAdmin.objects.filter(user=user).first()
#         serializer = EqubAdminDataSerializer(instance=equb_admin_obj)

#     return Response(
#         {"message": "success", "token": token.key, "data": serializer.data},
#         status=status.HTTP_200_OK,
#     )


# # @api_view(["GET"])
# # @authentication_classes([TokenAuthentication])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def test_token(request):
# #     return Response({"message": f"success for {request.user.phone}"})


# # @api_view(["GET"])
# # @authentication_classes([TokenAuthentication])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def adminGetAll(request):
# #     if request.method == "GET":
# #         admins = Admin.objects.all()
# #         serializer = AdminSerializer(admins, many=True)
# #         return Response(serializer.data, status=status.HTTP_200_OK)
