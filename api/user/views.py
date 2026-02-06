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
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
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
# CUSTOMER SIGNUP
# =========================
@api_view(["POST"])
@permission_classes([AllowAny])
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

    user = User.objects.create_customer(phone, password, email)
    token = Token.objects.create(user=user)

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
            "access_token": token.key,
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )
    
# =========================
# LOGIN (PHONE BASED) with token
# =========================
@api_view(["POST"])
def loginWithToken(request):
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

    if user.is_customer:
        serializer = CustomerDataSerializer(
            Customer.objects.get(user=user)
        )
    elif user.is_admin:
        serializer = AdminSerializer(
            Admin.objects.get(user=user)
        )
    elif user.is_equb_admin:
        serializer = EqubAdminDataSerializer(
            EqubAdmin.objects.get(user=user)
        )
    else:
        serializer = UserSerializer(user)

    return Response(
        {
            "message": "success",
            "data": serializer.data,
        },
        status=status.HTTP_200_OK,
    )