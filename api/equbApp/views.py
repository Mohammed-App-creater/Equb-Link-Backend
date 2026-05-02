# views.py
from django.utils import timezone
import uuid
from django.shortcuts import get_object_or_404
from django.urls import reverse
import requests
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from .models import (
    EqubType,
    EqubCategory,
    Equb,
    EqubMember,
    Payment,
    LotteryWinner,
    Notification,
    SupportTicket,
)
from .serializers import (
    EqubTypeSerializer,
    EqubCategorySerializer,
    EqubSerializer,
    EqubMemberSerializer,
    OwnerBankAccountPublicSerializer,
    PaymentSerializer,
    LotteryWinnerSerializer,
    NotificationSerializer,
    SupportTicketSerializer,
    EqubCategoryWithCountSerializer,
)
from .pagination import StandardResultsSetPagination
from rest_framework.pagination import PageNumberPagination
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import EqubMember, Payment, LotteryWinner, Notification, Equb
from .serializers import PaymentSerializer, LotteryWinnerSerializer, NotificationSerializer
from django.contrib.auth import get_user_model
from django.db.models import Q


# ----------------- Helper function -----------------
def paginated_response(queryset, serializer_class, request, filters=None):
    if filters:
        queryset = queryset.filter(**filters)
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return paginator.get_paginated_response({"data": serializer.data, "message": "Get successfully"})

User = get_user_model()


def notify_admins(message, notif_type="system"):
    """
    Send notification to all admin users
    """
    admins = User.objects.filter(
        Q(is_superuser=True) |
        Q(is_admin=True) |
        Q(is_equb_admin=True)
    )


    notifications = [
        Notification(
            user=admin,
            notif_type=notif_type,
            message=message
        )
        for admin in admins
    ]

    Notification.objects.bulk_create(notifications)


# =========================== EqubType ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_type_list_create_admin(request):
    if request.method == "GET":
        return paginated_response(EqubType.objects.all(), EqubTypeSerializer, request)
    elif request.method == "POST":
        serializer = EqubTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_type_detail_admin(request, id):
    instance = get_object_or_404(EqubType, id=id)
    if request.method == "GET":
        serializer = EqubTypeSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = EqubTypeSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
    



# =========================== EqubCategory ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_category_list_create_admin(request):
    if request.method == "GET":
        return paginated_response(EqubCategory.objects.all(), EqubCategorySerializer, request)
    elif request.method == "POST":
        serializer = EqubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_category_detail_admin(request, id):
    instance = get_object_or_404(EqubCategory, id=id)
    if request.method == "GET":
        serializer = EqubCategorySerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = EqubCategorySerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== Equb ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_list_create_admin(request):
    if request.method == "GET":
        return paginated_response(Equb.objects.all(), EqubSerializer, request)
    elif request.method == "POST":
        data = request.data.copy()
        data["owner"] = request.user.id
        serializer = EqubSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_detail_admin(request, id):
    instance = get_object_or_404(Equb, id=id)
    if request.method == "GET":
        serializer = EqubSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = EqubSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== EqubMember ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_member_list_create_admin(request):
    if request.method == "GET":
        filters = {}
        equb_id = request.GET.get("equb")
        user_id = request.GET.get("user")
        if equb_id: filters["equb__id"] = equb_id
        if user_id: filters["user__id"] = user_id
        return paginated_response(EqubMember.objects.all(), EqubMemberSerializer, request, filters=filters)
    elif request.method == "POST":
        serializer = EqubMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_member_detail_admin(request, id):
    instance = get_object_or_404(EqubMember, id=id)
    if request.method == "GET":
        serializer = EqubMemberSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = EqubMemberSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== Payment ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def payment_list_create_admin(request):
    if request.method == "GET":
        filters = {}
        equb_member_id = request.GET.get("equb_member")
        round_number = request.GET.get("round_number")
        if equb_member_id: filters["equb_member__id"] = equb_member_id
        if round_number: filters["round_number"] = round_number
        return paginated_response(Payment.objects.all(), PaymentSerializer, request, filters=filters)
    elif request.method == "POST":
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def payment_detail_admin(request, id):
    instance = get_object_or_404(Payment, id=id)
    if request.method == "GET":
        serializer = PaymentSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = PaymentSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== LotteryWinner ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def lottery_winner_list_create_admin(request):
    if request.method == "GET":
        filters = {}
        equb_id = request.GET.get("equb")
        round_number = request.GET.get("round_number")
        if equb_id: filters["equb__id"] = equb_id
        if round_number: filters["round_number"] = round_number
        return paginated_response(LotteryWinner.objects.all(), LotteryWinnerSerializer, request, filters=filters)
    elif request.method == "POST":
        serializer = LotteryWinnerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def lottery_winner_detail_admin(request, id):
    instance = get_object_or_404(LotteryWinner, id=id)
    if request.method == "GET":
        serializer = LotteryWinnerSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = LotteryWinnerSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== Notification ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def notification_list_create_admin(request):
    if request.method == "GET":
        filters = {}
        user_id = request.GET.get("user")
        if user_id: filters["user__id"] = user_id
        return paginated_response(Notification.objects.all(), NotificationSerializer, request, filters=filters)
    elif request.method == "POST":
        serializer = NotificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def notification_detail_admin(request, id):
    instance = get_object_or_404(Notification, id=id)
    if request.method == "GET":
        serializer = NotificationSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = NotificationSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# =========================== SupportTicket ===========================
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def support_ticket_list_create_admin(request):
    if request.method == "GET":
        filters = {}
        user_id = request.GET.get("user")
        status_filter = request.GET.get("status")
        if user_id: filters["user__id"] = user_id
        if status_filter: filters["status"] = status_filter
        return paginated_response(SupportTicket.objects.all(), SupportTicketSerializer, request, filters=filters)
    elif request.method == "POST":
        serializer = SupportTicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Created successfully"}, status=status.HTTP_201_CREATED)
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def support_ticket_detail_admin(request, id):
    instance = get_object_or_404(SupportTicket, id=id)
    if request.method == "GET":
        serializer = SupportTicketSerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})
    elif request.method == "PUT":
        serializer = SupportTicketSerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data": serializer.data, "message": "Updated successfully"})
        return Response({"data": serializer.errors, "message": "Error"}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == "DELETE":
        instance.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)




# =========================== Create a mobile-friendly API endpoint: ===========================

@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Only authenticated users can access
def equb_categories_with_count(request):
    # Order by 'is_favorite' first (True first), then by name
    categories = EqubCategory.objects.all().order_by('-is_favorite', 'name')
    
    result = []
    for category in categories:
        # Full image URL
        image_url = request.build_absolute_uri(category.image.url) if category.image else None

        # Total equbs (only active ones)
        total_active_equbs = category.equbs.filter(status="active").count()

        result.append({
            'category': {
                'id': category.id,
                'name': category.name,
                'image': image_url,
                'description': category.description,
                'total_equbs': total_active_equbs,
                'is_favorite': category.is_favorite
            }
        })

    return Response({
        "data": result,
        "message": "Categories with total Equbs fetched successfully"
    })
    
    
    

# -------------------- Pagination --------------------
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # default page size
    page_size_query_param = 'page_size'
    max_page_size = 100

# -------------------- Get Active Equbs by Category --------------------
@api_view(['GET'])
def get_active_equbs_by_category(request):
    """
    Returns all EqubCategories with their active Equbs and EqubType info.
    Each Equb also includes the current number of users who joined.
    Pagination supported.
    """
    categories = EqubCategory.objects.all()

    result = []

    for category in categories:
        active_equbs = category.equbs.filter(status="active")

        equb_list = []
        for equb in active_equbs:
            equb_data = EqubSerializer(equb).data

            # Add EqubType info
            equb_type_data = None
            if equb.equb_type:
                equb_type_data = EqubTypeSerializer(equb.equb_type).data

            equb_data['equb_type'] = equb_type_data

            # Current active members count
            equb_data['current_members_count'] = equb.members.filter(status="active").count()

            equb_list.append(equb_data)

        # Full image URL
        image_url = None
        if category.image:
            image_url = request.build_absolute_uri(category.image.url)

        result.append({
            'category': {
                'id': category.id,
                'name': category.name,
                'image': image_url,
                'description': category.description,
                'total_equbs': active_equbs.count(),
            },
            'equbs': equb_list
        })

    # Pagination
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(result, request)

    return paginator.get_paginated_response(page)


# -------------------- Get Active Equbs by Category_ID --------------------



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_equbs_by_category_id(request, category_id):
    """
    Returns all active Equbs for a specific category ID with:
    - EqubType info
    - Current number of active members
    - Total rounds
    - Current round
    """
    category = get_object_or_404(EqubCategory, id=category_id)
    active_equbs = category.equbs.filter(status="active")

    equb_list = []
    for equb in active_equbs:
        equb_data = EqubSerializer(equb).data

        # Add EqubType info
        equb_data['equb_type'] = EqubTypeSerializer(equb.equb_type).data if equb.equb_type else None

        # Current active members count
        equb_data['current_members_count'] = equb.members.filter(status="active").count()

        # Total rounds = total members
        equb_data['total_rounds'] = equb.total_members

        # Current round based on completed lottery winners
        completed_rounds = equb.lotterywinner_set.count()
        equb_data['current_round'] = completed_rounds + 1 if completed_rounds < equb.total_members else equb.total_members

        equb_list.append(equb_data)

    # Full category image URL
    image_url = request.build_absolute_uri(category.image.url) if category.image else None

    result = {
        'category': {
            'id': category.id,
            'name': category.name,
            'image': image_url,
            'description': category.description,
            'total_equbs': active_equbs.count(),
        },
        'equbs': equb_list
    }

    return Response({
        "data": result,
        "message": "Active Equbs fetched successfully"
    })


    
# -------------------- Get Active Equbs by equb_type_id --------------------

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_equbs_by_type_id(request, equb_type_id):
    """
    Returns all active Equbs for a specific EqubType (by ID).
    Each Equb includes EqubType info and current number of active members.
    Pagination supported.
    """
    try:
        eq_type = EqubType.objects.get(id=equb_type_id)
    except EqubType.DoesNotExist:
        return Response({"error": "EqubType not found"}, status=404)

    # Get active Equbs for this type
    active_equbs = Equb.objects.filter(status="active", equb_type=eq_type)

    equb_list = []
    for equb in active_equbs:
        equb_data = EqubSerializer(equb).data

        # Add EqubType info
        equb_data['equb_type'] = EqubTypeSerializer(eq_type).data

        # Current active members count
        equb_data['current_members_count'] = equb.members.filter(status="active").count()

        # Full category image URL if exists
        equb_data['category_image'] = (
            request.build_absolute_uri(equb.category.image.url)
            if equb.category.image else None
        )

        equb_list.append(equb_data)

    result = {
        'equb_type': {
            'id': eq_type.id,
            'name': eq_type.name,
            'description': eq_type.description
        },
        'equbs': equb_list
    }

    # Pagination
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(equb_list, request)
    return paginator.get_paginated_response({
        'equb_type': result['equb_type'],
        'equbs': page
    })
    
# API: List all members in a specific Equb

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def equb_members_list(request, equb_id):
    """
    Returns all members who joined a specific Equb
    """
    try:
        equb = Equb.objects.get(id=equb_id)
    except Equb.DoesNotExist:
        return Response({"error": "Equb not found"}, status=404)

    members = equb.members.all()
    serializer = EqubMemberSerializer(members, many=True)
    return Response({
        "equb_id": equb.id,
        "equb_name": equb.name,
        "members": serializer.data
    })
    

# API: Calculate Join Cost for an Equb

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def equb_join_cost(request, equb_id):
    equb = get_object_or_404(Equb, id=equb_id, status="active")

    completed_rounds = LotteryWinner.objects.filter(equb=equb).count()
    current_round = completed_rounds + 1

    total_required_amount = completed_rounds * equb.contribution_amount

    return Response({
        "equb_id": equb.id,
        "equb_name": equb.name,
        "current_round": current_round,
        "completed_rounds": completed_rounds,
        "contribution_per_round": equb.contribution_amount,
        "total_amount_to_pay": total_required_amount
    })

# API: Join an Equb

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_equb_initial(request, equb_id):
    """
    Join an active Equb before it has started (Round 0).
    Requires first-round payment.
    Admin approval required.
    """
    user = request.user

    # 1. Accept terms
    if not request.data.get("accept_terms"):
        return Response(
            {"message": "You must accept the terms and conditions."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Get active Equb
    equb = get_object_or_404(Equb, id=equb_id, status="active")

    # 3. Prevent duplicate join
    if EqubMember.objects.filter(user=user, equb=equb).exists():
        return Response(
            {"message": "You already joined this Equb."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. Check if Equb has started
    completed_rounds = LotteryWinner.objects.filter(equb=equb).count()
    if completed_rounds > 0:
        return Response(
            {"message": "Equb already started. Use standard join flow."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 5. Check capacity (active + pending)
    total_members = EqubMember.objects.filter(equb=equb).count()
    if total_members >= equb.total_members:
        return Response(
            {"message": "This Equb is already full."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 6. Validate payment input (first round payment)
    amount = request.data.get("amount")
    payment_method = request.data.get("payment_method")
    transaction_id = request.data.get("transaction_id")
    receipt_image = request.FILES.get("receipt_image")

    if not all([amount, payment_method, transaction_id, receipt_image]):
        return Response(
            {"message": "Payment details are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if float(amount) != float(equb.contribution_amount):
        return Response(
            {
                "message": "Incorrect payment amount.",
                "required_amount": equb.contribution_amount
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # 7. Create pending EqubMember
    membership = EqubMember.objects.create(
        user=user,
        equb=equb,
        status="pending",
        payment_status="pending"
    )

    # 8. Create pending payment (Round 0)
    Payment.objects.create(
        equb_member=membership,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        receipt_image=receipt_image,
        status="pending",
        round_number=0
    )
    
    Notification.objects.create(
        user=user,
        notif_type="join_request_submitted",
        message=(
            f"Your join request for {equb.name} has been submitted. "
            f"First-round payment is pending admin approval."
        )
    )
    
    # Notify admins
    notify_admins(
        message=(
            f"New join request (initial) from {user.phone} "
            f"for Equb: {equb.name}"
        ),
        notif_type="join_request"
    )


    return Response(
        {
            "message": "Join request submitted. First-round payment pending admin approval.",
            "equb": equb.name,
            "paid_round": 0,
            "member_status": membership.status
        },
        status=status.HTTP_201_CREATED
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_equb(request, equb_id):
    """
    Join an active Equb already in progress.
    New member must pay total contribution for all completed rounds.
    Admin approval required before activation.
    """
    user = request.user

    # 1. Accept terms
    if not request.data.get("accept_terms"):
        return Response(
            {"message": "You must accept the terms and conditions."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Get active Equb
    equb = get_object_or_404(Equb, id=equb_id, status="active")

    # 3. Prevent duplicate join
    if EqubMember.objects.filter(user=user, equb=equb).exists():
        return Response(
            {"message": "You already joined this Equb."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 4. Check capacity (ACTIVE members only)
    active_members = EqubMember.objects.filter(
        equb=equb, status="active"
    ).count()

    if active_members >= equb.total_members:
        return Response(
            {"message": "This Equb is already full."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 5. Calculate completed rounds
    completed_rounds = LotteryWinner.objects.filter(equb=equb).count()

    if completed_rounds == 0:
        return Response(
            {"message": "Equb has not started yet. Use normal join flow."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 6. Calculate total amount required
    total_amount_required = completed_rounds * equb.contribution_amount

    # 7. Validate payment input
    amount = request.data.get("amount")
    payment_method = request.data.get("payment_method")
    transaction_id = request.data.get("transaction_id")
    receipt_image = request.FILES.get("receipt_image")

    if not all([amount, payment_method, transaction_id, receipt_image]):
        return Response(
            {"message": "Payment details are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if float(amount) != float(total_amount_required):
        return Response(
            {
                "message": f"Incorrect payment amount.",
                "required_amount": total_amount_required,
                "completed_rounds": completed_rounds
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # 8. Create pending EqubMember
    membership = EqubMember.objects.create(
        user=user,
        equb=equb,
        status="pending",
        payment_status="pending"
    )

    # 9. Create aggregated payment record
    Payment.objects.create(
        equb_member=membership,
        amount=amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        receipt_image=receipt_image,
        status="pending",
        round_number=completed_rounds  # represents payment up to this round
    )
    
    
    Notification.objects.create(
        user=user,
        notif_type="join_request_submitted",
        message=(
            f"Your join request for {equb.name} has been submitted. "
            f"You paid for {completed_rounds} previous rounds. "
            f"Admin approval is required."
        )
    )
    
    # Notify admins
    notify_admins(
        message=(
            f"New join request from {user.phone} "
            f"for Equb: {equb.name} "
            f"(Paid {completed_rounds} rounds)"
        ),
        notif_type="join_request"
    )


    return Response(
        {
            "message": (
                f"Join request submitted. You paid for "
                f"{completed_rounds} previous rounds. "
                f"Admin approval is required."
            ),
            "equb": equb.name,
            "completed_rounds": completed_rounds,
            "total_paid": total_amount_required,
            "member_status": membership.status
        },
        status=status.HTTP_201_CREATED
    )


# Admin Approval API

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # Admin-only
def approve_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)

    # Only pending payments
    if payment.status != "pending":
        return Response({"error": "Payment already processed."}, status=400)

    # Approve payment
    payment.status = "completed"
    payment.save()

    # Activate member
    member = payment.equb_member
    member.status = "active"
    member.payment_status = "paid"
    member.save()

    return Response({"message": "Payment approved. Member is now active in the Equb."})


@api_view(['GET'])
def list_pending_payments(request):
    pending_payments = Payment.objects.filter(status="pending")
    serializer = PaymentSerializer(pending_payments, many=True)
    return Response({"pending_payments": serializer.data})




# API: Customer Dashboard

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_dashboard(request):
    """
    Returns the logged-in customer's:
    1. Total contribution per Equb
    2. Contribution per round
    3. Payment history
    4. Lottery wins per round
    5. Notifications
    6. equb member
    """
    user = request.user

    #  All Equbs the user joined
    equb_memberships = EqubMember.objects.filter(user=user).select_related("equb").prefetch_related(
        "equb__payout_bank_accounts",
    )

    equbs_data = []

    for membership in equb_memberships:
        equb = membership.equb

        # Total contributed
        total_contribution = membership.payments.aggregate(total=Sum('amount'))['total'] or 0

        # Payment history per round
        payments = Payment.objects.filter(equb_member=membership).order_by('round_number')
        payments_data = PaymentSerializer(payments, many=True).data

        # Lottery win history per round
        winnings = LotteryWinner.objects.filter(equb=equb, winner=membership)
        winnings_data = LotteryWinnerSerializer(winnings, many=True).data

        payout_list = OwnerBankAccountPublicSerializer(
            equb.payout_bank_accounts.all(), many=True
        ).data

        equbs_data.append({
            "equb_id": equb.id,
            "equb_name": equb.name,
            "status": equb.status,
            "payout_bank_accounts": payout_list,
            "total_contribution": total_contribution,
            "payment_history": payments_data,
            "winnings": winnings_data,
        })

    # 2️⃣ Notifications
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    notifications_data = NotificationSerializer(notifications, many=True).data

    return Response({
        "user_id": user.id,
        "user_name": user.phone,
        "equbs": equbs_data,
        "notifications": notifications_data,
        "message": "Customer dashboard fetched successfully"
    })

    
# Helper function to get current round number

def get_current_round(equb):
    last_winner = LotteryWinner.objects.filter(equb=equb).order_by("-round_number").first()
    return last_winner.round_number + 1 if last_winner else 1
 
def get_next_unpaid_round(member):
    paid_rounds = member.payments.filter(status="completed").values_list("round_number", flat=True)
    current_round = get_current_round(member.equb)

    for r in range(1, current_round + 1):
        if r not in paid_rounds:
            return r
    return None

# API: Pay Equb Contribution for Current Round

def _get_chapa_user_names(user):
    """Get first_name and last_name for Chapa from user profile. Safe fallbacks."""
    full_name = None
    if hasattr(user, "customer") and user.customer:
        full_name = user.customer.name
    elif hasattr(user, "admin") and user.admin:
        full_name = user.admin.name
    elif hasattr(user, "equbadmin") and user.equbadmin:
        full_name = user.equbadmin.name
    if not full_name:
        full_name = user.phone or "Member"
    name_parts = str(full_name).strip().split(None, 1)
    first = name_parts[0] if name_parts else "Equb"
    last = name_parts[1] if len(name_parts) > 1 else "Member"
    return first, last


def _get_chapa_email(user):
    """Get email for Chapa; fallback to phone-based if missing."""
    email = (user.email or "").strip() or None
    if not email:
        safe_phone = (user.phone or "").replace("+", "").replace(" ", "").strip()
        email = f"{safe_phone}@equb.app"
    return email


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pay_equb_contribution(request, equb_id):
    """
    Pay Equb contribution for the next unpaid round.
    Supports:
    - payment_method == "chapa": online Chapa flow; no transaction_id/receipt_image.
    - other methods: manual receipt; requires transaction_id and receipt_image.
    """
    user = request.user

    equb = get_object_or_404(Equb, id=equb_id, status="active")
    member = get_object_or_404(EqubMember, user=user, equb=equb, status="active")

    next_round = get_next_unpaid_round(member)
    if not next_round:
        return Response({
            "message": "All contributions are already paid."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Prevent duplicate payment for same round
    if Payment.objects.filter(equb_member=member, round_number=next_round).exists():
        return Response({
            "message": "A payment for this round has already been submitted."
        }, status=status.HTTP_400_BAD_REQUEST)

    payment_method = (request.data.get("payment_method") or "").strip().lower()

    if payment_method == "chapa":
        # --- Chapa flow: no transaction_id or receipt_image ---
        tx_ref = f"equb-{uuid.uuid4()}"
        amount = equb.contribution_amount

        payment = Payment.objects.create(
            equb_member=member,
            amount=amount,
            transaction_id=tx_ref,
            round_number=next_round,
            status="pending",
            payment_method="chapa"
        )

        first_name, last_name = _get_chapa_user_names(user)
        email = _get_chapa_email(user)
        callback_url = request.build_absolute_uri(reverse("chapa-callback"))
        return_url = request.build_absolute_uri("/payment-success/")

        payload = {
            "amount": str(amount),
            "currency": "ETB",
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url
        }
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}

        try:
            response = requests.post(
                "https://api.chapa.co/v1/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=10
            )
            data = response.json()
        except requests.RequestException:
            payment.delete()
            return Response({
                "message": "Payment initialization failed. Please try again."
            }, status=status.HTTP_502_BAD_GATEWAY)

        if not response.ok or data.get("status") != "success":
            payment.delete()
            return Response({
                "message": data.get("message", "Chapa payment initialization failed.")
            }, status=status.HTTP_400_BAD_REQUEST)

        checkout_url = (data.get("data") or {}).get("checkout_url", "")
        if not checkout_url:
            payment.delete()
            return Response({
                "message": "Invalid response from payment provider."
            }, status=status.HTTP_502_BAD_GATEWAY)

        Notification.objects.create(
            user=user,
            notif_type="payment_submitted",
            message=(
                f"Your Chapa payment for {equb.name} (Round {next_round}) has been initiated. "
                f"Complete payment at the checkout link."
            )
        )
        notify_admins(
            message=(
                f"Chapa payment initiated by {user.phone} "
                f"for Equb: {equb.name} (Round {next_round})"
            ),
            notif_type="payment_submitted"
        )

        return Response({
            "message": "Redirect user to checkout_url to complete payment.",
            "checkout_url": checkout_url,
            "tx_ref": tx_ref,
            "amount": float(amount),
            "round": next_round
        }, status=status.HTTP_201_CREATED)

    # --- Manual receipt flow ---
    transaction_id = request.data.get("transaction_id")
    receipt_image = request.FILES.get("receipt_image")
    if not payment_method:
        return Response({
            "message": "payment_method is required."
        }, status=status.HTTP_400_BAD_REQUEST)
    if not transaction_id or not receipt_image:
        return Response({
            "message": "transaction_id and receipt_image are required for non-Chapa payments."
        }, status=status.HTTP_400_BAD_REQUEST)

    Payment.objects.create(
        equb_member=member,
        amount=equb.contribution_amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        receipt_image=receipt_image,
        round_number=next_round,
        status="pending"
    )

    Notification.objects.create(
        user=user,
        notif_type="payment_submitted",
        message=(
            f"Your payment for {equb.name} "
            f"(Round {next_round}) has been submitted and is pending admin approval."
        )
    )
    notify_admins(
        message=(
            f"New payment submitted by {user.phone} "
            f"for Equb: {equb.name} (Round {next_round})"
        ),
        notif_type="payment_submitted"
    )

    return Response({
        "message": f"Payment submitted for round {next_round}. Awaiting approval.",
        "round": next_round,
        "amount": equb.contribution_amount
    }, status=status.HTTP_201_CREATED)


# API: Pay Equb Contribution via Chapa (dedicated endpoint)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pay_equb_contribution_chapa(request, equb_id):
    """
    Pay next unpaid round via Chapa. No transaction_id or receipt_image required.
    Returns checkout_url for redirect; Chapa callback updates payment status.
    """
    # Step 1: Get user
    user = request.user

    # Step 2: Get active Equb
    equb = get_object_or_404(Equb, id=equb_id, status="active")

    # Step 3: Verify membership
    member = get_object_or_404(EqubMember, user=user, equb=equb, status="active")

    # Step 4: Get next unpaid round
    next_round = get_next_unpaid_round(member)
    if not next_round:
        return Response(
            {"message": "All contributions are already paid."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 5: Prevent duplicate payment (pending or completed for this round)
    if Payment.objects.filter(
        equb_member=member,
        round_number=next_round,
        status__in=["pending", "completed"]
    ).exists():
        return Response(
            {"message": "Payment already initiated for this round."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Step 6: Generate Chapa transaction reference (Chapa max 50 chars)
    tx_ref = f"equb-contribution-{uuid.uuid4().hex}"

    # Step 7: Create pending Payment
    payment = Payment.objects.create(
        equb_member=member,
        amount=equb.contribution_amount,
        payment_method="chapa",
        transaction_id=tx_ref,
        round_number=next_round,
        status="pending"
    )

    # Step 8: Prepare user info for Chapa
    full_name = None
    if hasattr(user, "customer") and user.customer:
        full_name = user.customer.name
    elif hasattr(user, "admin") and user.admin:
        full_name = user.admin.name
    elif hasattr(user, "equbadmin") and user.equbadmin:
        full_name = user.equbadmin.name
    else:
        full_name = user.phone

    name_parts = str(full_name or "").strip().split(None, 1)
    first_name = name_parts[0] if name_parts else "Equb"
    last_name = name_parts[1] if len(name_parts) > 1 else "Member"

   # Step 9: Build Chapa payload
    payload = {
        "amount": str(equb.contribution_amount),
        "currency": "ETB",
        "first_name": first_name,
        "last_name": last_name,
        "tx_ref": tx_ref,
        "callback_url": request.build_absolute_uri(reverse("chapa-callback")),
        "return_url": request.build_absolute_uri("/payment-success/")
    }

    # Only add email if user actually has a real one
    if user.email:
        payload["email"] = user.email

    # ✅ This line was missing
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    # Step 10: Call Chapa API
    try:
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()
        
            # ✅ Add these two lines to see the real error
        print("Chapa status code:", response.status_code)
        print("Chapa response:", data)
        
    except requests.RequestException:
        payment.delete()
        return Response(
            {"message": "Payment initialization failed. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY
        )

    # Step 11: Handle response
    if not response.ok or data.get("status") != "success":
        payment.delete()
        print("Chapa status code:", response.status_code)
        print("Chapa response:", data)
        return Response(
            {"message": data.get("message", "Chapa payment initialization failed.")},
            status=status.HTTP_400_BAD_REQUEST
        )

    checkout_url = (data.get("data") or {}).get("checkout_url", "")
    if not checkout_url:
        payment.delete()
        return Response(
            {"message": "Invalid response from payment provider."},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response({
        "message": "Redirect user to checkout_url",
        "checkout_url": checkout_url,
        "tx_ref": tx_ref,
        "amount": equb.contribution_amount,
        "round": next_round
    }, status=status.HTTP_201_CREATED)


# Admin API: Approve or Reject Payment
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_approve_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, status="pending")
    member = payment.equb_member

    action = request.data.get("action")  # approve | reject

    if action not in ["approve", "reject"]:
        return Response({
            "message": "Action must be 'approve' or 'reject'"
        }, status=status.HTTP_400_BAD_REQUEST)

    if action == "approve":
        payment.status = "completed"
        payment.paid_at = timezone.now()
        payment.save()

        # Update member payment status
        member.payment_status = "paid"
        member.save(update_fields=["payment_status"])

        Notification.objects.create(
            user=member.user,
            notif_type="payment_approved",
            message=(
                f"Your payment for {member.equb.name} "
                f"(Round {payment.round_number}) has been approved."
            )
        )

        return Response({
            "message": "Payment approved successfully."
        })

    # Reject
    payment.status = "pending"
    payment.save()

    Notification.objects.create(
        user=member.user,
        notif_type="payment_rejected",
        message=(
            f"Your payment for {member.equb.name} "
            f"(Round {payment.round_number}) was rejected. "
            f"Please upload a valid receipt."
        )
    )

    return Response({
        "message": "Payment rejected."
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def equb_detail(request, id):
    """
    Returns detailed information for a single Equb:
    - Basic info
    - EqubType info
    - Category info
    - Member counts
    - Members
    - Winners
    - Round progress
    """
    equb = get_object_or_404(
        Equb.objects.prefetch_related("payout_bank_accounts"),
        id=id,
    )
    
    # Serialize basic info
    data = EqubSerializer(equb).data
    
    # Add Type info
    if equb.equb_type:
        data['equb_type'] = EqubTypeSerializer(equb.equb_type).data
    
    # Add Category info
    if equb.category:
        category_data = EqubCategorySerializer(equb.category).data
        if equb.category.image:
            category_data['image'] = request.build_absolute_uri(equb.category.image.url)
        data['category'] = category_data

    # Add member stats
    data['current_members_count'] = equb.members.filter(status="active").count()
    data['total_rounds'] = equb.total_members
    data['members_list'] = EqubMemberSerializer(equb.members.all(), many=True).data
    data['winners_list'] = LotteryWinnerSerializer(equb.lotterywinner_set.all(), many=True).data
    
    # Calculate current round
    completed_rounds = equb.lotterywinner_set.count()
    data['current_round'] = completed_rounds + 1 if completed_rounds < equb.total_members else equb.total_members
    
    return Response({
        "data": data,
        "message": "Equb details fetched successfully"
    })

# Payment success page (for Chapa return_url)
def payment_success(request):
    return render(request, "payment_success.html")


# =========================== Customer Notifications ===========================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def customer_notifications(request):
    """
    Returns a paginated list of notifications for the logged-in user.
    """
    notifications = Notification.objects.filter(user=request.user).order_by("-created_at")
    return paginated_response(notifications, NotificationSerializer, request)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_notification_as_read(request):
    """
    Marks specific notifications as read.
    Expects a list of IDs in the request body: {"ids": ["uuid1", "uuid2"]}
    """
    ids = request.data.get("ids")
    if not ids or not isinstance(ids, list):
        return Response(
            {"message": "A list of notification IDs is required."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    updated_count = Notification.objects.filter(user=request.user, id__in=ids).update(is_read=True)
    
    return Response({
        "message": f"{updated_count} notifications marked as read.",
        "updated_count": updated_count
    })

 
 
#  =========================== Chapa payment ===========================
 
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def initialize_chapa_payment(request):
    equb_member_id = request.data.get("equb_member")
    amount = request.data.get("amount")
    round_number = request.data.get("round_number")

    tx_ref = f"equb-{uuid.uuid4()}"

    payment = Payment.objects.create(
        equb_member_id=equb_member_id,
        amount=amount,
        transaction_id=tx_ref,
        round_number=round_number,
        status="pending",
        payment_method="chapa"
    )

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": "user@email.com",
        "first_name": "Equb",
        "last_name": "Member",
        "tx_ref": tx_ref,
        "callback_url": "https://yourdomain.com/api/chapa/callback/",
        "return_url": "https://yourdomain.com/payment-success/"
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.post(
        "https://api.chapa.co/v1/transaction/initialize",
        json=payload,
        headers=headers,
        timeout=10  # seconds
    )

    data = response.json()

    payment.chapa_checkout_url = data["data"]["checkout_url"]
    payment.save()

    return Response({
        "checkout_url": payment.chapa_checkout_url,
        "tx_ref": tx_ref
    })
    
@api_view(["GET"])
def verify_chapa_payment(request, tx_ref):
    payment = Payment.objects.get(transaction_id=tx_ref)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(
        f"https://api.chapa.co/v1/transaction/verify/{tx_ref}",
        headers=headers,
        timeout=10  # seconds
    )

    data = response.json()

    if data["status"] == "success":
        payment.status = "completed"
        payment.paid_at = timezone.now()
        payment.save()

        return Response({"status": "completed"})

    payment.status = "rejected"
    payment.save()

    return Response({"status": "failed"})


# ===========================
# Join Equb via Chapa
# ===========================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join_equb_chapa(request, equb_id):
    """
    Join an Equb and pay via Chapa.
    - Initial join (round 0): amount = equb.contribution_amount
    - Ongoing join: amount = completed_rounds * equb.contribution_amount
    Returns checkout_url and tx_ref for redirecting user to Chapa payment.
    """
    user = get_user_model().objects.get(pk=request.user.pk)

    # 1. Get active Equb
    equb = get_object_or_404(Equb, id=equb_id)
    if equb.status != "active":
        return Response(
            {"message": "This Equb is not active."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Prevent duplicate join
    if EqubMember.objects.filter(user=user, equb=equb).exists():
        return Response(
            {"message": "You already joined this Equb."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 3. Determine initial vs ongoing
    completed_rounds = LotteryWinner.objects.filter(equb=equb).count()
    is_initial_join = completed_rounds == 0

    # 4. Calculate amount
    if is_initial_join:
        amount = equb.contribution_amount
        round_number = 0
    else:
        amount = completed_rounds * equb.contribution_amount
        round_number = completed_rounds

    # 5. Check Equb capacity
    if is_initial_join:
        total_members = EqubMember.objects.filter(equb=equb).count()
        if total_members >= equb.total_members:
            return Response(
                {"message": "This Equb is already full."},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        active_members = EqubMember.objects.filter(equb=equb, status="active").count()
        if active_members >= equb.total_members:
            return Response(
                {"message": "This Equb is already full."},
                status=status.HTTP_400_BAD_REQUEST
            )

    # 6. Create pending EqubMember
    membership = EqubMember.objects.create(
        user=user,
        equb=equb,
        status="pending",
        payment_status="pending"
    )

    # 7. Generate unique tx_ref for Chapa
    tx_ref = f"equb-{uuid.uuid4()}"

    # 8. Create pending Payment (for Chapa callback to update)
    payment = Payment.objects.create(
        equb_member=membership,
        amount=amount,
        transaction_id=tx_ref,
        round_number=round_number,
        status="pending",
        payment_method="chapa"
    )

    # 9. Build Chapa payload (email and name for Chapa)
    email = _get_chapa_email(user)
    first, last = _get_chapa_user_names(user)

    # Chapa will call this URL and pass trx_ref as query param
    callback_url = request.build_absolute_uri(reverse("chapa-callback"))
    return_url = request.build_absolute_uri("/payment-success/")

    payload = {
        "amount": str(amount),
        "currency": "ETB",
        "email": email,
        "first_name": first,
        "last_name": last,
        "tx_ref": tx_ref,
        "callback_url": callback_url,
        "return_url": return_url
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    # 10. Call Chapa initialize API
    try:
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()
    except requests.RequestException as e:
        # Cleanup on failure
        payment.delete()
        membership.delete()
        return Response(
            {"message": "Payment initialization failed. Please try again."},
            status=status.HTTP_502_BAD_GATEWAY
        )

    if not response.ok or data.get("status") != "success":
        
        payment.delete()
        membership.delete()
        return Response(
            {"message": data.get("message", "Chapa payment initialization failed.")},
            status=status.HTTP_400_BAD_REQUEST
        )

    checkout_url = data.get("data", {}).get("checkout_url", "")
    if not checkout_url:
        payment.delete()
        membership.delete()
        return Response(
            {"message": "Invalid response from payment provider."},
            status=status.HTTP_502_BAD_GATEWAY
        )

    return Response({
        "message": "Redirect user to checkout_url to complete payment.",
        "checkout_url": checkout_url,
        "tx_ref": tx_ref,
        "amount": float(amount),
        "round_number": round_number,
        "equb_name": equb.name
    }, status=status.HTTP_201_CREATED)


@api_view(["GET", "POST"])
def chapa_callback(request):
    tx_ref = request.GET.get("trx_ref") or request.data.get("trx_ref")

    if not tx_ref:
        return Response({"error": "Missing tx_ref"}, status=400)

    try:
        payment = Payment.objects.get(transaction_id=tx_ref)
    except Payment.DoesNotExist:
        return Response({"error": "Payment not found"}, status=404)

    # Verify with Chapa
    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(
        f"https://api.chapa.co/v1/transaction/verify/{tx_ref}",
        headers=headers,
        timeout=10
    )

    data = response.json()

    if data.get("status") == "success":
        payment.status = "completed"
        payment.paid_at = timezone.now()
        payment.save()

        return Response({"status": "completed"})

    payment.status = "rejected"
    payment.save()

    return Response({"status": "failed"})