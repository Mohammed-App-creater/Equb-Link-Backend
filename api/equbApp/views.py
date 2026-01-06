# views.py
import uuid
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

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
    PaymentSerializer,
    LotteryWinnerSerializer,
    NotificationSerializer,
    SupportTicketSerializer,EqubCategoryWithCountSerializer,
)
from .pagination import StandardResultsSetPagination
from rest_framework.pagination import PageNumberPagination
    
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum
from .models import EqubMember, Payment, LotteryWinner, Notification, Equb
from .serializers import PaymentSerializer, LotteryWinnerSerializer, NotificationSerializer

# ----------------- Helper function -----------------
def paginated_response(queryset, serializer_class, request, filters=None):
    if filters:
        queryset = queryset.filter(**filters)
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    serializer = serializer_class(page, many=True)
    return paginator.get_paginated_response({"data": serializer.data, "message": "Get successfully"})


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
    """
    user = request.user

    #  All Equbs the user joined
    equb_memberships = EqubMember.objects.filter(user=user).select_related('equb')

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

        equbs_data.append({
            "equb_id": equb.id,
            "equb_name": equb.name,
            "status": equb.status,
            "total_contribution": total_contribution,
            "payment_history": payments_data,
            "winnings": winnings_data,
        })

    # 2️⃣ Notifications
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    notifications_data = NotificationSerializer(notifications, many=True).data

    return Response({
        "user_id": user.id,
        "user_name": user.name,
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def pay_equb_contribution(request, equb_id):
    user = request.user

    equb = get_object_or_404(Equb, id=equb_id, status="active")
    member = get_object_or_404(EqubMember, user=user, equb=equb, status="active")

    current_round = get_current_round(equb)
    next_round = get_next_unpaid_round(member)

    if not next_round:
        return Response({
            "message": "All contributions are already paid."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Validate request
    payment_method = request.data.get("payment_method")
    transaction_id = request.data.get("transaction_id")
    receipt_image = request.FILES.get("receipt_image")

    if not all([payment_method, transaction_id, receipt_image]):
        return Response({
            "message": "payment_method, transaction_id, and receipt_image are required."
        }, status=status.HTTP_400_BAD_REQUEST)

    # Create payment
    Payment.objects.create(
        equb_member=member,
        amount=equb.contribution_amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        receipt_image=receipt_image,
        round_number=next_round,
        status="pending"
    )

    return Response({
        "message": f"Payment submitted for round {next_round}. Awaiting approval.",
        "round": next_round,
        "amount": equb.contribution_amount
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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
# from django.shortcuts import get_object_or_404
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# from django.db.models import Count, Sum, Q
# from datetime import timedelta
# from django.utils import timezone
# import random

# from user.permissions import IsAdminUser, IsCustomerUser
# from .models import (
#     Equb, EqubCategory,  EqubType, 
#     EqubMember, Payment, LotteryWinner, Notification, SupportTicket
# )
# from .serializers import (
#     EqubSerializer, EqubCategorySerializer, 
#     EqubTypeSerializer, EqubMemberSerializer, 
#     EqubPostSerializer, 
#     EqubMemberPostSerializer, EqubMemberDataSerializer,
#     PaymentSerializer
# )
# from user.models import User

# # ---------------------- EqubType ----------------------

# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_type_list_create_admin(request):
#     if request.method == "GET":
#         types = EqubType.objects.all()
#         serializer = EqubTypeSerializer(types, many=True)
#         return Response(
#             {"data": serializer.data, "message": "Get successfully"},
#             status=status.HTTP_200_OK,
#         )

#     elif request.method == "POST":
#         serializer = EqubTypeSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Created successfully"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# @api_view(["GET", "PUT", "DELETE"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_type_detail_admin(request, id):
#     instance = get_object_or_404(EqubType, id=id)

#     if request.method == "GET":
#         serializer = EqubTypeSerializer(instance)
#         return Response({"data": serializer.data, "message": "Get successfully"})

#     elif request.method == "PUT":
#         serializer = EqubTypeSerializer(instance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Updated successfully"}
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     elif request.method == "DELETE":
#         instance.delete()
#         return Response(
#             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
#         )


# # ---------------------- EqubCategory ----------------------
# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_category_list_create_admin(request):
#     if request.method == "GET":
#         categories = EqubCategory.objects.all()
#         serializer = EqubCategorySerializer(categories, many=True)
#         return Response({"data": serializer.data, "message": "Get successfully"})

#     elif request.method == "POST":
#         serializer = EqubCategorySerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Created successfully"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# @api_view(["GET", "PUT", "DELETE"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_category_detail_admin(request, id):
#     instance = get_object_or_404(EqubCategory, id=id)

#     if request.method == "GET":
#         serializer = EqubCategorySerializer(instance)
#         return Response({"data": serializer.data, "message": "Get successfully"})

#     elif request.method == "PUT":
#         serializer = EqubCategorySerializer(instance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Updated successfully"}
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     elif request.method == "DELETE":
#         instance.delete()
#         return Response(
#             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
#         )





# # ---------------------- Equb ----------------------
# @api_view(["GET", "POST"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_list_create_admin(request):
#     if request.method == "GET":
#         equbs = Equb.objects.all()
#         serializer = EqubSerializer(equbs, many=True)
#         return Response({"data": serializer.data, "message": "Get successfully"})

#     elif request.method == "POST":
#         data = request.data.copy()
#         data["owner"] = str(request.user.id)
#         serializer = EqubPostSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Created successfully"},
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )


# @api_view(["GET", "PUT", "DELETE"])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_detail_admin(request, id):
#     instance = get_object_or_404(Equb, id=id)

#     if request.method == "GET":
#         serializer = EqubSerializer(instance)
#         return Response({"data": serializer.data, "message": "Get successfully"})

#     elif request.method == "PUT":
#         serializer = EqubSerializer(instance, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(
#                 {"data": serializer.data, "message": "Updated successfully"}
#             )
#         return Response(
#             {"data": serializer.errors, "message": "Error"},
#             status=status.HTTP_400_BAD_REQUEST,
#         )

#     elif request.method == "DELETE":
#         instance.delete()
#         return Response(
#             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
#         )
        



# @api_view(["GET"])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def equb_list_customer(request):
#     equbs = Equb.objects.all()
#     serializer = EqubSerializer(equbs, many=True)
#     return Response({"data": serializer.data, "message": "Get successfully"})


# # ---------------------- categories with Equbs ----------------------
# @api_view(['GET'])
# def subcategories_with_equbs_by_category(request, category_id):
#     try:
#         subcategories = EqubSubCategory.objects.filter(category__id=category_id)

#         if not subcategories.exists():
#             return Response({
#                 "data": [],
#                 "message": "No subcategories found for this category."
#             }, status=status.HTTP_404_NOT_FOUND)

#         subcategory_data = []

#         for subcat in subcategories:
#             equbs = Equb.objects.filter(subcategory=subcat).annotate(
#                 total_members=Count('members', distinct=True),
#                 total_payout=Sum(
#                     'members__payments__amount',
#                     filter=Q(members__payments__status='completed'),
#                     default=0
#                 )
#             )

#             subcat_serialized = SubCategoryWithEqubsSerializer(subcat)
#             equb_serialized = EqubSerializer(equbs, many=True)

#             subcategory_data.append({
#                 "id": subcat.id,
#                 "name": subcat.name,
#                 "description": subcat.description,
#                 "image": request.build_absolute_uri(subcat.image.url) if subcat.image else None,
#                 "equbs": equb_serialized.data
#             })

#         return Response({
#             "data": subcategory_data,
#             "message": "Fetched successfully"
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             "data": [],
#             "message": f"An error occurred: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- Equbs by subcategory ----------------------
# @api_view(["GET"])
# def equbs_by_subcategory(request, subcategory_id):
#     try:
#         equbs = Equb.objects.filter(subcategory__id=subcategory_id)
#         serializer = EqubSerializer(equbs, many=True)
#         return Response({
#             "data": serializer.data,
#             "message": "Equbs fetched successfully"
#         }, status=status.HTTP_200_OK)
#     except Exception as e:
#         return Response({
#             "error": str(e),
#             "message": "An error occurred"
#         }, status=status.HTTP_400_BAD_REQUEST)


# # ---------------------- Equbs user joined ----------------------
# @api_view(["GET"])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def equbs_user_joined(request):
#     equb_memberships = EqubMember.objects.filter(user=request.user)
#     equbs = Equb.objects.filter(id__in=equb_memberships.values_list("equb_id", flat=True))
#     serializer = EqubSerializer(equbs, many=True)
#     return Response(
#         {"data": serializer.data, "message": "Equbs joined by user retrieved successfully"},
#         status=status.HTTP_200_OK
#     )


# # ---------------------- Join Equb ----------------------
# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def join_equb(request):
#     try:
#         user_id = request.data.get('user')
#         equb_id = request.data.get('equb')
        
#         user = User.objects.get(id=user_id)
#         equb = Equb.objects.get(id=equb_id)

#         # Check if user is already a member
#         if EqubMember.objects.filter(user=user, equb=equb).exists():
#             return Response({
#                 "message": "User is already a member of this Equb."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Check if equb has reached maximum members
#         current_members = EqubMember.objects.filter(equb=equb, status="active").count()
#         if current_members >= equb.total_members:
#             return Response({
#                 "message": "Equb has reached maximum members."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Create new member
#         new_member = EqubMember.objects.create(
#             user=user,
#             equb=equb,
#             status='active',
#             payment_status='pending',
#             has_received_payout=False
#         )

#         serializer = EqubMemberPostSerializer(new_member)
#         return Response({
#             "data": serializer.data,
#             "message": "User successfully joined the Equb."
#         }, status=status.HTTP_201_CREATED)

#     except User.DoesNotExist:
#         return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Equb.DoesNotExist:
#         return Response({"message": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- Get Equb Members ----------------------
# @api_view(['GET'])
# def equb_members(request, equb_id):
#     try:
#         equb = Equb.objects.get(id=equb_id)
#         members = EqubMember.objects.filter(equb=equb)
        
#         response_data = []
#         for member in members:
#             member_data = EqubMemberDataSerializer(member).data
#             member_data['customer_name'] = member.user.full_name
            
#             response_data.append(member_data)

#         return Response({
#             "data": response_data,
#             "message": "Fetched Equb members successfully."
#         }, status=status.HTTP_200_OK)

#     except Equb.DoesNotExist:
#         return Response({
#             "message": "Equb not found."
#         }, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({
#             "message": f"An error occurred: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- Unjoin Equb ----------------------
# @api_view(['POST'])
# def unjoin_equb(request):
#     try:
#         user_id = request.data.get('user')
#         equb_id = request.data.get('equb')

#         user = User.objects.get(id=user_id)
#         equb = Equb.objects.get(id=equb_id)

#         equb_member = EqubMember.objects.filter(user=user, equb=equb).first()
#         if not equb_member:
#             return Response({
#                 "message": "User is not a member of this Equb."
#             }, status=status.HTTP_400_BAD_REQUEST)

#         # Instead of deleting, mark as removed
#         equb_member.status = "removed"
#         equb_member.save()

#         return Response({
#             "message": "User successfully unjoined the Equb."
#         }, status=status.HTTP_200_OK)

#     except User.DoesNotExist:
#         return Response({
#             "message": "User not found."
#         }, status=status.HTTP_404_NOT_FOUND)
#     except Equb.DoesNotExist:
#         return Response({
#             "message": "Equb not found."
#         }, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({
#             "message": f"An error occurred: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- List Equb Members ----------------------
# @api_view(['GET'])
# def list_equb_members(request, equb_id):
#     members = EqubMember.objects.filter(equb_id=equb_id)
#     serializer = EqubMemberSerializer(members, many=True)
#     return Response({
#         "data": serializer.data,
#         "message": f"Members of Equb ID {equb_id} retrieved successfully"
#     }, status=status.HTTP_200_OK)


# # ---------------------- Preview Equb Winner ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def preview_equb_winner(request, equb_id):
#     try:
#         equb = Equb.objects.get(id=equb_id)
#     except Equb.DoesNotExist:
#         return Response({"error": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)

#     # Get IDs of already selected winners
#     winners = LotteryWinner.objects.filter(equb=equb).values_list('winner_id', flat=True)

#     # Get eligible members who haven't won yet and have paid
#     eligible_members = EqubMember.objects.filter(
#         equb=equb,
#         status='active',
#         payment_status='paid'
#     ).exclude(id__in=winners)

#     if not eligible_members.exists():
#         return Response({"message": "No eligible members left to win."}, status=status.HTTP_400_BAD_REQUEST)

#     # Randomly select one eligible member
#     selected_member = random.choice(list(eligible_members))
    
#     return Response({
#         "message": f"{selected_member.user.full_name} is selected as a potential winner.",
#         "winner": {
#             "user_id": str(selected_member.user.id),
#             "name": selected_member.user.full_name,
#             "equb_member_id": str(selected_member.id),
#             "equb_id": str(equb.id),
#         }
#     }, status=status.HTTP_200_OK)


# # ---------------------- Confirm and Save Winner ----------------------
# @api_view(['POST'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def confirm_and_save_winner(request):
#     user_id = request.data.get('user')
#     equb_member_id = request.data.get('equb_member')
#     equb_id = request.data.get('equb')

#     if not equb_id or not equb_member_id:
#         return Response({"error": "equb_id and equb_member_id are required."}, 
#                        status=status.HTTP_400_BAD_REQUEST)

#     equb = get_object_or_404(Equb, id=equb_id)
#     equb_member = get_object_or_404(EqubMember, id=equb_member_id, equb=equb)
    
#     # Check if the member has already won
#     already_won = LotteryWinner.objects.filter(
#         equb=equb, 
#         winner=equb_member
#     ).exists()
    
#     if already_won:
#         return Response({"message": "This member has already won before."}, 
#                        status=status.HTTP_400_BAD_REQUEST)

#     # Check round number
#     current_round = LotteryWinner.objects.filter(equb=equb).count() + 1
    
#     # Create a new lottery winner entry
#     winner = LotteryWinner.objects.create(
#         equb=equb,
#         winner=equb_member,
#         round_number=current_round,
#         draw_date=timezone.now()
#     )

#     # Mark member as having received payout
#     equb_member.has_received_payout = True
#     equb_member.save()

#     # Handle lottery_draw_schedule update logic based on EqubType
#     equb_type = equb.equb_type
    
#     if equb_type:
#         if equb_type.name.lower() == 'daily':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(days=1)
#         elif equb_type.name.lower() == 'weekly':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=1)
#         elif equb_type.name.lower() == 'monthly':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(days=30)
#         elif equb_type.name.lower() == '2 months':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(days=60)
#         elif equb_type.name.lower() == '3 months':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(days=90)
#         elif equb_type.name.lower() == '6 months':
#             next_draw_date = equb.lottery_draw_schedule + timedelta(days=180)
#         else:
#             next_draw_date = equb.lottery_draw_schedule

#         # Update lottery draw schedule if within end date
#         if next_draw_date <= equb.end_date:
#             equb.lottery_draw_schedule = next_draw_date
#             next_draw_info = str(next_draw_date)
#         else:
#             equb.status = "completed"
#             next_draw_info = "Completed - No more draws"
        
#         equb.save()
#     else:
#         next_draw_info = "EqubType not found"

#     return Response({
#         "message": f"{equb_member.user.full_name} has been saved as the winner for round {current_round}.",
#         "draw_date": winner.draw_date,
#         "next_draw_schedule": next_draw_info,
#         "round_number": current_round
#     }, status=status.HTTP_201_CREATED)


# # ---------------------- User Equb Payment Summary ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def user_equb_payment_summary(request, user_id):
#     memberships = EqubMember.objects.filter(user_id=user_id)

#     if not memberships.exists():
#         return Response({"message": "User is not a member of any Equb."}, 
#                        status=status.HTTP_404_NOT_FOUND)

#     result = []
#     for member in memberships:
#         total_payment = Payment.objects.filter(
#             equb_member=member, 
#             status='completed'
#         ).aggregate(total=Sum('amount'))['total'] or 0
        
#         result.append({
#             "equb_id": str(member.equb.id),
#             "equb_name": member.equb.name,
#             "total_paid": float(total_payment),
#             "round_number": Payment.objects.filter(
#                 equb_member=member, 
#                 status='completed'
#             ).count()
#         })

#     return Response({
#         "user_id": user_id,
#         "payment_summary": result,
#         "message": "Payment summary fetched successfully."
#     }, status=status.HTTP_200_OK)


# # ---------------------- User Payment History ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def list_user_payment_history(request, user_id):
#     equb_members = EqubMember.objects.filter(user_id=user_id)

#     if not equb_members.exists():
#         return Response({
#             "message": "No Equb memberships found for this user."
#         }, status=status.HTTP_404_NOT_FOUND)

#     payments = Payment.objects.filter(
#         equb_member__in=equb_members
#     ).select_related('equb_member', 'equb_member__equb')

#     payments = payments.order_by('-paid_at')
#     serializer = PaymentSerializer(payments, many=True)

#     return Response({
#         "user_id": user_id,
#         "payment_history": serializer.data,
#         "message": "User payment history retrieved successfully."
#     }, status=status.HTTP_200_OK)


# # ---------------------- Equb Detailed Report ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def equb_detailed_report(request, equb_id):
#     try:
#         equb = Equb.objects.get(id=equb_id)
#         members = EqubMember.objects.filter(equb=equb)
#         member_ids = members.values_list('id', flat=True)

#         # Fetch paid members
#         paid_members = Payment.objects.filter(
#             equb_member__in=member_ids, 
#             status='completed'
#         ).values_list('equb_member', flat=True).distinct()
        
#         unpaid_members = members.exclude(id__in=paid_members)

#         # Fetch winners
#         winner_member_ids = LotteryWinner.objects.filter(
#             equb=equb
#         ).values_list('winner_id', flat=True)
        
#         winners = members.filter(id__in=winner_member_ids)
#         unwinners = members.exclude(id__in=winner_member_ids)

#         data = {
#             "equb_name": equb.name,
#             "equb_status": equb.status,
#             "total_members": members.count(),
#             "paid_members_count": paid_members.count(),
#             "unpaid_members_count": unpaid_members.count(),
#             "winners_count": winners.count(),
#             "unwinners_count": unwinners.count(),
#             "paid_members": [
#                 {
#                     "full_name": m.user.full_name,
#                     "status": m.status,
#                     "joined_at": m.joined_at
#                 } for m in members.filter(id__in=paid_members)
#             ],
#             "unpaid_members": [
#                 {
#                     "full_name": m.user.full_name,
#                     "status": m.status,
#                     "joined_at": m.joined_at
#                 } for m in unpaid_members
#             ],
#             "winners": [
#                 {
#                     "full_name": m.user.full_name,
#                     "draw_date": LotteryWinner.objects.get(
#                         equb=equb, 
#                         winner=m
#                     ).draw_date
#                 } for m in winners
#             ],
#             "unwinners": [
#                 {
#                     "full_name": m.user.full_name,
#                 } for m in unwinners
#             ]
#         }

#         return Response({"message": "Equb detailed report", "data": data}, 
#                        status=status.HTTP_200_OK)

#     except Equb.DoesNotExist:
#         return Response({"message": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({"message": f"Error: {str(e)}"}, 
#                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- Admin Equb Report ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsAdminUser])
# def admin_equb_report(request):
#     try:
#         report = {
#             "total_equbs": Equb.objects.count(),
#             "total_equb_members": EqubMember.objects.count(),
#             "total_equb_categories": EqubCategory.objects.count(),
#             "total_equb_subcategories": EqubSubCategory.objects.count(),

#             "equbs_per_status": Equb.objects.values('status').annotate(total=Count('id')),
#             "equbs_per_category": Equb.objects.values('subcategory__category__name').annotate(total=Count('id')),
#             "equbs_per_subcategory": Equb.objects.values('subcategory__name').annotate(total=Count('id')),

#             "active_members": EqubMember.objects.filter(status='active').count(),
#             "inactive_members": EqubMember.objects.filter(status='inactive').count(),
#             "removed_members": EqubMember.objects.filter(status='removed').count(),

#             "pending_payments": Payment.objects.filter(status='pending').count(),
#             "completed_payments": Payment.objects.filter(status='completed').count(),
#             "total_payment_amount": Payment.objects.filter(
#                 status='completed'
#             ).aggregate(total=Sum('amount'))['total'] or 0,

#             "lottery_winners": LotteryWinner.objects.count(),
#             "support_tickets_open": SupportTicket.objects.filter(status='open').count(),
#             "support_tickets_in_progress": SupportTicket.objects.filter(status='in_progress').count(),
#             "support_tickets_resolved": SupportTicket.objects.filter(status='resolved').count(),
#         }

#         return Response({
#             "message": "Admin report generated successfully",
#             "data": report
#         }, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({
#             "message": f"Failed to generate report: {str(e)}",
#             "data": {}
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # ---------------------- Customer Total Payment for Equb ----------------------
# @api_view(['GET'])
# def customer_total_payment_for_equb(request, equb_id, user_id):
#     try:
#         equb = Equb.objects.get(id=equb_id)
#     except Equb.DoesNotExist:
#         return Response({"detail": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)

#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#     try:
#         member = EqubMember.objects.get(equb=equb, user=user)
#     except EqubMember.DoesNotExist:
#         return Response({"detail": "User is not a member of the specified Equb."}, 
#                        status=status.HTTP_404_NOT_FOUND)

#     total_paid = Payment.objects.filter(
#         equb_member=member, 
#         status='completed'
#     ).aggregate(total=Sum('amount'))['total'] or 0.00

#     return Response({
#         "equb_id": str(equb.id),
#         "equb_name": equb.name,
#         "user_id": str(user.id),
#         "email": user.email,
#         "full_name": user.full_name,
#         "total_paid": total_paid,
#         "payment_status": member.payment_status
#     })


# # ---------------------- Customer Equb Contributions ----------------------
# @api_view(['GET'])
# def customer_equb_contributions(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

#     contributions = []
#     equb_memberships = EqubMember.objects.filter(user=user)

#     for membership in equb_memberships:
#         total_paid = Payment.objects.filter(
#             equb_member=membership,
#             status='completed'
#         ).aggregate(total=Sum('amount'))['total'] or 0.00

#         contributions.append({
#             "equb_id": str(membership.equb.id),
#             "equb_name": membership.equb.name,
#             "equb_status": membership.equb.status,
#             "member_status": membership.status,
#             "has_received_payout": membership.has_received_payout,
#             "total_paid": total_paid
#         })

#     return Response({
#         "user_id": str(user.id),
#         "email": user.email,
#         "full_name": user.full_name,
#         "equb_contributions": contributions
#     })


# # ---------------------- Admin View Equbs with Members ----------------------
# @api_view(['GET'])
# @permission_classes([IsAdminUser])
# def admin_view_equbs_with_members(request):
#     equbs = Equb.objects.all().prefetch_related('members')
#     serializer = EqubSerializer(equbs, many=True)
#     return Response(serializer.data)


# # ---------------------- Upload Receipt ----------------------
# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def upload_receipt(request, equb_member_id):
#     try:
#         equb_member = EqubMember.objects.get(id=equb_member_id, user=request.user)
#     except EqubMember.DoesNotExist:
#         return Response({"error": "Equb member not found."}, status=status.HTTP_404_NOT_FOUND)

#     receipt_image = request.FILES.get('receipt_image')
#     if not receipt_image:
#         return Response({"error": "Receipt image is required."}, status=status.HTTP_400_BAD_REQUEST)

#     # Get current round number
#     current_round = Payment.objects.filter(
#         equb_member=equb_member
#     ).count() + 1

#     payment = Payment.objects.create(
#         equb_member=equb_member,
#         amount=request.data.get("amount", equb_member.equb.payment_per_round),
#         payment_method=request.data.get("payment_method", "manual"),
#         transaction_id=request.data.get("transaction_id"),
#         receipt_image=receipt_image,
#         status='pending',
#         round_number=current_round
#     )

#     return Response({
#         "message": "Receipt uploaded successfully.",
#         "payment_id": str(payment.id),
#         "round_number": current_round
#     }, status=status.HTTP_201_CREATED)


# # ---------------------- Get Draw Countdown ----------------------
# @api_view(['GET'])
# @permission_classes([IsAuthenticated, IsCustomerUser])
# def get_draw_countdown(request, equb_id):
#     equb = get_object_or_404(Equb, id=equb_id)
    
#     if equb.lottery_draw_schedule is None:
#         return Response({
#             "message": "No lottery draw schedule set for this Equb.",
#             "next_draw_schedule": None,
#             "countdown": None
#         }, status=status.HTTP_200_OK)

#     # Calculate countdown
#     now = timezone.now()
#     if equb.lottery_draw_schedule.date() < now.date():
#         # Draw date has passed
#         if equb.status == "completed":
#             return Response({
#                 "message": "Equb is completed.",
#                 "next_draw_schedule": "Completed",
#                 "countdown": None
#             })
        
#         # Calculate next draw based on equb type
#         equb_type = equb.equb_type
#         if equb_type:
#             if equb_type.name.lower() == 'daily':
#                 next_draw = now + timedelta(days=1)
#             elif equb_type.name.lower() == 'weekly':
#                 next_draw = now + timedelta(weeks=1)
#             elif equb_type.name.lower() == 'monthly':
#                 next_draw = now + timedelta(days=30)
#             elif equb_type.name.lower() == '2 months':
#                 next_draw = now + timedelta(days=60)
#             elif equb_type.name.lower() == '3 months':
#                 next_draw = now + timedelta(days=90)
#             elif equb_type.name.lower() == '6 months':
#                 next_draw = now + timedelta(days=180)
#             else:
#                 next_draw = equb.lottery_draw_schedule
#         else:
#             next_draw = equb.lottery_draw_schedule
#     else:
#         next_draw = equb.lottery_draw_schedule

#     # Calculate time difference
#     time_difference = next_draw - now
    
#     if time_difference.total_seconds() <= 0:
#         countdown_str = "Draw time!"
#     else:
#         days = time_difference.days
#         hours = time_difference.seconds // 3600
#         minutes = (time_difference.seconds % 3600) // 60
#         seconds = time_difference.seconds % 60
        
#         countdown_str = f"{days}d {hours}h {minutes}m {seconds}s"

#     return Response({
#         "next_draw_schedule": next_draw.strftime('%Y-%m-%d %H:%M:%S'),
#         "countdown": countdown_str,
#         "equb_status": equb.status
#     }, status=status.HTTP_200_OK)

# # from django.shortcuts import get_object_or_404
# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.response import Response
# # from rest_framework import status

# # from user.permissions import IsAdminUser, IsCustomerUser
# # from .models import Equb, EqubCategory,  EqubType,EqubMember
# # from .serializers import (
# #     EqubSerializer,
# #     EqubCategorySerializer,
# #     
# #     EqubTypeSerializer,
# #     EqubMemberSerializer,
# #     EqubSubCategoryPostSerializer,
# #     EqubPostSerializer,
# #     SubCategoryWithEqubsSerializer,
# #     EqubMemberPostSerializer,
# #     EqubMemberDataSerializer
# # )
# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.response import Response
# # from rest_framework import status
# # from django.db.models import Count, Sum
# # from .models import Equb, EqubMember, Payment, LotteryWinner, SupportTicket, EqubCategory, EqubSubCategory

# # from django.db.models.signals import post_save
# # from django.dispatch import receiver
# # from .models import LotteryWinner, Notification
# # from django.utils import timezone
# # from django.contrib.auth import get_user_model

# # User = get_user_model()  # This will fetch the custom User model dynamically

# # # ---------------------- EqubType ----------------------

# # @api_view(["GET", "POST"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_type_list_create_admin(request):
# #     if request.method == "GET":
# #         types = EqubType.objects.all()
# #         serializer = EqubTypeSerializer(types, many=True)
# #         return Response(
# #             {"data": serializer.data, "message": "Get successfully"},
# #             status=status.HTTP_200_OK,
# #         )

# #     elif request.method == "POST":
# #         serializer = EqubTypeSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Created successfully"},
# #                 status=status.HTTP_201_CREATED,
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )


# # @api_view(["GET", "PUT", "DELETE"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_type_detail_admin(request, id):
# #     instance = get_object_or_404(EqubType, id=id)

# #     if request.method == "GET":
# #         serializer = EqubTypeSerializer(instance)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "PUT":
# #         serializer = EqubTypeSerializer(instance, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Updated successfully"}
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )

# #     elif request.method == "DELETE":
# #         instance.delete()
# #         return Response(
# #             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
# #         )


# # # ---------------------- EqubCategory ----------------------
# # @api_view(["GET", "POST"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_category_list_create_admin(request):
# #     if request.method == "GET":
# #         categories = EqubCategory.objects.all()
# #         serializer = EqubCategorySerializer(categories, many=True)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "POST":
# #         serializer = EqubCategorySerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Created successfully"},
# #                 status=status.HTTP_201_CREATED,
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )


# # @api_view(["GET", "PUT", "DELETE"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_category_detail_admin(request, id):
# #     instance = get_object_or_404(EqubCategory, id=id)

# #     if request.method == "GET":
# #         serializer = EqubCategorySerializer(instance)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "PUT":
# #         serializer = EqubCategorySerializer(instance, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Updated successfully"}
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )

# #     elif request.method == "DELETE":
# #         instance.delete()
# #         return Response(
# #             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
# #         )


# # # ---------------------- EqubSubCategory ----------------------
# # @api_view(["GET", "POST"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_subcategory_list_create_admin(request):
# #     if request.method == "GET":
# #         subcategories = EqubSubCategory.objects.all()
# #         serializer = subcategories, many=True)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "POST":
# #         serializer = EqubSubCategoryPostSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Created successfully"},
# #                 status=status.HTTP_201_CREATED,
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )


# # @api_view(["GET", "PUT", "DELETE"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_subcategory_detail_admin(request, id):
# #     instance = get_object_or_404( id=id)

# #     if request.method == "GET":
# #         serializer = instance)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "PUT":
# #         serializer = instance, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Updated successfully"}
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )

# #     elif request.method == "DELETE":
# #         instance.delete()
# #         return Response(
# #             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
# #         )


# # # ---------------------- Equb ----------------------

# # @api_view(["GET", "POST"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_list_create_admin(request):
# #     if request.method == "GET":
# #         equbs = Equb.objects.all()
# #         serializer = EqubSerializer(equbs, many=True)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "POST":
# #         data = request.data.copy()
# #         data["owner"] = str(request.user.id)  # set the owner to the logged-in user
# #         serializer = EqubPostSerializer(data=data)
# #         # serializer = EqubPostSerializer(data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Created successfully"},
# #                 status=status.HTTP_201_CREATED,
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )


# # @api_view(["GET"])
# # @permission_classes([IsAuthenticated, IsCustomerUser])
# # def equb_list_customer(request):
# #     equbs = Equb.objects.all()
# #     serializer = EqubSerializer(equbs, many=True)
# #     return Response({"data": serializer.data, "message": "Get successfully"})


# # @api_view(["GET", "PUT", "DELETE"])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_detail_admin(request, id):
# #     instance = get_object_or_404(Equb, id=id)

# #     if request.method == "GET":
# #         serializer = EqubSerializer(instance)
# #         return Response({"data": serializer.data, "message": "Get successfully"})

# #     elif request.method == "PUT":
# #         serializer = EqubSerializer(instance, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(
# #                 {"data": serializer.data, "message": "Updated successfully"}
# #             )
# #         return Response(
# #             {"data": serializer.errors, "message": "Error"},
# #             status=status.HTTP_400_BAD_REQUEST,
# #         )

# #     elif request.method == "DELETE":
# #         instance.delete()
# #         return Response(
# #             {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
# #         )
# # # To list all EqubSubCategory by EqubCategory ID, you can create a Django REST API endpoint like this:
# # @api_view(["GET"])
# # @permission_classes([IsAuthenticated])
# # def list_subcategories_by_category(request, category_id):
# #     """
# #     List all EqubSubCategory by category ID
# #     """
# #     category = get_object_or_404(EqubCategory, id=category_id)
# #     subcategories = EqubSubCategory.objects.filter(category=category)
# #     serializer = subcategories, many=True)
# #     return Response(
# #         {"data": serializer.data, "message": "Subcategories fetched successfully"},
# #         status=status.HTTP_200_OK
# #     )


# # from django.db.models import Count, Sum, Q
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import EqubCategory,  Equb, Payment
# # from .serializers import SubCategoryWithEqubsSerializer, EqubSerializer

# # @api_view(['GET'])
# # def subcategories_with_equbs_by_category(request, category_id):
# #     try:
# #         subcategories = EqubSubCategory.objects.filter(category__id=category_id)

# #         if not subcategories.exists():
# #             return Response({
# #                 "data": [],
# #                 "message": "No subcategories found for this category."
# #             }, status=status.HTTP_404_NOT_FOUND)

# #         subcategory_data = []

# #         for subcat in subcategories:
# #             # Annotate each equb under this subcategory with total members and completed payment total
# #             equbs = Equb.objects.filter(subcategory=subcat).annotate(
# #                 total_members=Count('equbmember', distinct=True),
# #                 total_payout=Sum(
# #                     'equbmember__payment__amount',
# #                     filter=Q(equbmember__payment__status='completed'),
# #                     default=0
# #                 )
# #             )

# #             subcat_serialized = SubCategoryWithEqubsSerializer(subcat)
# #             equb_serialized = EqubSerializer(equbs, many=True)

# #             subcategory_data.append({
# #                 "id": subcat.id,
# #                 "name": subcat.name,
# #                 "description": subcat.description,
# #                 "image": request.build_absolute_uri(subcat.image.url) if subcat.image else None,
# #                 "equbs": equb_serialized.data
# #             })

# #         return Response({
# #             "data": subcategory_data,
# #             "message": "Fetched successfully"
# #         }, status=status.HTTP_200_OK)

# #     except Exception as e:
# #         return Response({
# #             "data": [],
# #             "message": f"An error occurred: {str(e)}"
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # @api_view(["GET"])
# # def equbs_by_subcategory(request, subcategory_id):
# #     try:
# #         equbs = Equb.objects.filter(subcategory__id=subcategory_id)
# #         serializer = EqubSerializer(equbs, many=True)
# #         return Response({
# #             "data": serializer.data,
# #             "message": "Equbs fetched successfully"
# #         }, status=status.HTTP_200_OK)
# #     except Exception as e:
# #         return Response({
# #             "error": str(e),
# #             "message": "An error occurred"
# #         }, status=status.HTTP_400_BAD_REQUEST)
    

# # #     Get all Equbs that the current authenticated user has joined.

# # @api_view(["GET"])
# # @permission_classes([IsAuthenticated,IsCustomerUser])
# # def equbs_user_joined(request):
# #     """
# #     Get all Equbs that the current authenticated user has joined.
# #     """
# #     equb_memberships = EqubMember.objects.filter(user=request.user)
# #     equbs = Equb.objects.filter(id__in=equb_memberships.values_list("equb_id", flat=True))
# #     serializer = EqubSerializer(equbs, many=True)
# #     return Response(
# #         {"data": serializer.data, "message": "Equbs joined by user retrieved successfully"},
# #         status=status.HTTP_200_OK
# #     )


# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated, IsCustomerUser])
# # def join_equb(request):
# #     try:
# #         # Extract the user and equb ID from the request data
# #         user_id = request.data.get('user')
# #         equb_id = request.data.get('equb')

# #         print(f"Received user_id: {user_id}, equb_id: {equb_id}")
        
# #         # Fetch the user and equb instances
# #         user = User.objects.get(id=user_id)
# #         equb = Equb.objects.get(id=equb_id)

# #         print(f"Found user: {user}, equb: {equb}")

# #         # Check if the user is already a member of the Equb
# #         if EqubMember.objects.filter(user=user, equb=equb).exists():
# #             return Response({
# #                 "message": "User is already a member of this Equb."
# #             }, status=status.HTTP_400_BAD_REQUEST)

# #         # Create a new EqubMember instance
# #         new_member = EqubMember.objects.create(
# #             user=user,
# #             equb=equb,
# #             total_members=equb.total_number_of_members,
# #             status='active',
# #             payment_status='pending'
# #         )

# #         # Update the rules_and_condit_status to True
# #         equb.rules_and_condit_status = True
# #         equb.save()

# #         # Serialize the newly created member and return
# #         serializer = EqubMemberPostSerializer(new_member)
# #         return Response({
# #             "data": serializer.data,
# #             "message": "User successfully joined the Equb. Rules and conditions confirmed."
# #         }, status=status.HTTP_201_CREATED)

# #     except User.DoesNotExist:
# #         return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
# #     except Equb.DoesNotExist:
# #         return Response({"message": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)
# #     except Exception as e:
# #         return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import Equb, EqubMember
# # from user.models import Customer
# # from .serializers import EqubMemberDataSerializer

# # @api_view(['GET'])
# # def equb_members(request, equb_id):
# #     try:
# #         # Fetch the Equb instance
# #         equb = Equb.objects.get(id=equb_id)

# #         # Fetch all members of the Equb
# #         members = EqubMember.objects.filter(equb=equb)

# #         # Create a list to hold serialized data
# #         response_data = []

# #         for member in members:
# #             # Fetch the corresponding Customer for each member
# #             customer = Customer.objects.get(user=member.user)
            
# #             # Serialize the member data and include customer name
# #             member_data = EqubMemberDataSerializer(member).data
# #             member_data['customer_name'] = customer.name  # Add customer name to the response data
            
# #             # Append to the response data list
# #             response_data.append(member_data)

# #         return Response({
# #             "data": response_data,
# #             "message": "Fetched Equb members successfully."
# #         }, status=status.HTTP_200_OK)

# #     except Equb.DoesNotExist:
# #         return Response({
# #             "message": "Equb not found."
# #         }, status=status.HTTP_404_NOT_FOUND)
# #     except Customer.DoesNotExist:
# #         return Response({
# #             "message": "Customer not found for one of the members."
# #         }, status=status.HTTP_404_NOT_FOUND)
# #     except Exception as e:
# #         return Response({
# #             "message": f"An error occurred: {str(e)}"
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# # @api_view(['POST'])
# # def unjoin_equb(request):
# #     try:
# #         # Extract the user and equb ID from the request data
# #         user_id = request.data.get('user')
# #         equb_id = request.data.get('equb')

# #         # Fetch the user and equb instances
# #         user = User.objects.get(id=user_id)
# #         equb = Equb.objects.get(id=equb_id)

# #         # Check if the user is a member of the Equb
# #         equb_member = EqubMember.objects.filter(user=user, equb=equb).first()
# #         if not equb_member:
# #             return Response({
# #                 "message": "User is not a member of this Equb."
# #             }, status=status.HTTP_400_BAD_REQUEST)

# #         # Delete the EqubMember record to unjoin
# #         equb_member.delete()

# #         # Return success response
# #         return Response({
# #             "message": "User successfully unjoined the Equb."
# #         }, status=status.HTTP_200_OK)

# #     except User.DoesNotExist:
# #         return Response({
# #             "message": "User not found."
# #         }, status=status.HTTP_404_NOT_FOUND)
# #     except Equb.DoesNotExist:
# #         return Response({
# #             "message": "Equb not found."
# #         }, status=status.HTTP_404_NOT_FOUND)
# #     except Exception as e:
# #         return Response({
# #             "message": f"An error occurred: {str(e)}"
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # # list all members for each equb

# # @api_view(['GET'])
# # def list_equb_members(request, equb_id):
# #     members = EqubMember.objects.filter(equb_id=equb_id)
# #     serializer = EqubMemberSerializer(members, many=True)
# #     return Response({
# #         "data": serializer.data,
# #         "message": f"Members of Equb ID {equb_id} retrieved successfully"
# #     }, status=status.HTTP_200_OK)


# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.response import Response
# # from rest_framework import status
# # import random

# # from .models import Equb, EqubMember, LotteryWinner
# # from user.models import Customer  # or the appropriate model for user info
# # from user.permissions import IsCustomerUser  # assuming you have this defined

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated, IsCustomerUser])
# # def preview_equb_winner(request, equb_id):
# #     try:
# #         equb = Equb.objects.get(id=equb_id)
# #     except Equb.DoesNotExist:
# #         return Response({"error": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)

# #     # Get IDs of already selected winners
# #     winners = LotteryWinner.objects.filter(equb=equb).values_list('winner_id', flat=True)

# #     # Get eligible members who haven't won yet
# #     eligible_members = EqubMember.objects.filter(
# #         equb=equb,
# #         status='active'
# #     ).exclude(user_id__in=winners)

# #     if not eligible_members.exists():
# #         return Response({"message": "No eligible members left to win."}, status=status.HTTP_400_BAD_REQUEST)

# #     # Randomly select one eligible member
# #     selected_member = random.choice(list(eligible_members))
# #     try:
# #         customer = Customer.objects.get(user=selected_member.user)
# #         selected_name = customer.name
# #     except Customer.DoesNotExist:
# #         selected_name = selected_member.user.email  # fallback to email if name not found

# #     return Response({
# #         "message": f"{selected_name} is selected as a potential winner.",
# #         "winner": {
# #             "user_id": str(selected_member.user.id),
# #             "name": selected_name,
# #             "equb_id": str(equb.id),
# #         }
# #     }, status=status.HTTP_200_OK)



# # # save  winner after it spin 

# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.response import Response
# # from rest_framework import status
# # from django.utils import timezone
# # from datetime import timedelta
# # from django.shortcuts import get_object_or_404
# # from .models import Equb, LotteryWinner  # use your correct import path



# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.decorators import api_view, permission_classes
# # from django.shortcuts import get_object_or_404
# # from django.utils import timezone
# # from datetime import timedelta
# # from .models import Equb, LotteryWinner, EqubType

# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated, IsCustomerUser])
# # def confirm_and_save_winner(request):
# #     user_id = request.data.get('user')
# #     equb_id = request.data.get('equb')

# #     if not equb_id or not user_id:
# #         return Response({"error": "equb_id and user_id are required."}, status=status.HTTP_400_BAD_REQUEST)

# #     equb = get_object_or_404(Equb, id=equb_id)
# #     user = get_object_or_404(User, id=user_id)

# #     # Ensure customer profile exists for the user
# #     try:
# #         customer = Customer.objects.get(user=user)
# #     except Customer.DoesNotExist:
# #         return Response({"error": "Customer profile not found for this user."}, status=status.HTTP_404_NOT_FOUND)

# #     # Check if the user has already won
# #     already_won = LotteryWinner.objects.filter(equb=equb, winner=user).exists()
# #     if already_won:
# #         return Response({"message": "This user has already won before."}, status=status.HTTP_400_BAD_REQUEST)

# #     # Create a new lottery winner entry
# #     winner = LotteryWinner.objects.create(
# #         equb=equb,
# #         winner=user,
# #         draw_date=timezone.now()
# #     )

# #     # Handle lottery_draw_schedule update logic based on EqubType
# #     equb_type = equb.subcategory.default_equb_type  # Assuming the `EqubSubCategory` links to `EqubType`
    
# #     if equb_type:
# #         if equb_type.name.lower() == 'daily':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(days=1)
# #         elif equb_type.name.lower() == 'weekly':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=1)
# #         elif equb_type.name.lower() == 'monthly':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=4)  # Approximation of a month
# #         elif equb_type.name.lower() == '2 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=8)  # Approximation of 2 months
# #         elif equb_type.name.lower() == '3 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=12)  # Approximation of 3 months
# #         elif equb_type.name.lower() == '6 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=24)  # Approximation of 6 months
# #         else:
# #             next_draw_date = equb.lottery_draw_schedule  # No change if type is unknown

# #         # Ensure the next draw is within the `end_date`
# #         if next_draw_date <= equb.end_date:
# #             equb.lottery_draw_schedule = next_draw_date
# #             equb.save()
# #             next_draw_info = str(next_draw_date)
# #         else:
# #             next_draw_info = "Completed - No more draws"

# #     else:
# #         next_draw_info = "EqubType not found"

# #     return Response({
# #         "message": f"{customer.name} has been saved as the winner.",
# #         "draw_date": winner.draw_date,
# #         "next_draw_schedule": next_draw_info
# #     }, status=status.HTTP_201_CREATED)








# # #     # Get all EqubMemberships for this user

# # from django.db.models import Sum
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import EqubMember, Payment

# # # list total contirbute money by each equb  

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated,IsCustomerUser])
# # def user_equb_payment_summary(request, user_id):
# #     # Get all EqubMemberships for this user
# #     memberships = EqubMember.objects.filter(user_id=user_id)

# #     if not memberships.exists():
# #         return Response({"message": "User is not a member of any Equb."}, status=status.HTTP_404_NOT_FOUND)

# #     # Prepare payment summary per Equb
# #     result = []
# #     for member in memberships:
# #         total_payment = Payment.objects.filter(equb_member=member, status='completed') \
# #                                        .aggregate(total=Sum('amount'))['total'] or 0
        
# #         result.append({
# #             "equb_id": str(member.equb.id),
# #             "equb_name": member.equb.name,
# #             "total_paid": float(total_payment),
# #         })

# #     return Response({
# #         "user_id": user_id,
# #         "payment_summary": result,
# #         "message": "Payment summary fetched successfully."
# #     }, status=status.HTTP_200_OK)


# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import EqubMember, Payment
# # from .serializers import PaymentSerializer  # Make sure this serializer exists


# # # list all the payement Hisotry of the user 

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated,IsCustomerUser])
# # def list_user_payment_history(request, user_id):
# #     # Get all EqubMember instances for the user
# #     equb_members = EqubMember.objects.filter(user_id=user_id)

# #     if not equb_members.exists():
# #         return Response({
# #             "message": "No Equb memberships found for this user."
# #         }, status=status.HTTP_404_NOT_FOUND)

# #     # Get all payments for these memberships
# #     payments = Payment.objects.filter(equb_member__in=equb_members).select_related('equb_member', 'equb_member__equb')

# #     # Optional: Order by most recent
# #     payments = payments.order_by('-paid_at')

# #     serializer = PaymentSerializer(payments, many=True)

# #     return Response({
# #         "user_id": user_id,
# #         "payment_history": serializer.data,
# #         "message": "User payment history retrieved successfully."
# #     }, status=status.HTTP_200_OK)


# # # admin report 

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated, IsAdminUser])
# # def equb_detailed_report(request, equb_id):
# #     try:
# #         # Fetch the Equb object
# #         equb = Equb.objects.get(id=equb_id)

# #         # Fetch members associated with the Equb
# #         members = EqubMember.objects.filter(equb=equb)
# #         member_ids = members.values_list('id', flat=True)

# #         # Fetch paid members
# #         paid_members = Payment.objects.filter(equb_member__in=member_ids, status='completed').values_list('equb_member', flat=True).distinct()
# #         unpaid_members = members.exclude(id__in=paid_members)

# #         # Fetch winners
# #         winner_user_ids = LotteryWinner.objects.filter(equb=equb).values_list('winner_id', flat=True)
# #         winners = members.filter(user_id__in=winner_user_ids)
# #         unwinners = members.exclude(user_id__in=winner_user_ids)

# #         # Prepare the report data
# #         data = {
# #             "equb_name": equb.name,
# #             "total_members": members.count(),
# #             "paid_members_count": paid_members.count(),
# #             "unpaid_members_count": unpaid_members.count(),
# #             "winners_count": winners.count(),
# #             "unwinners_count": unwinners.count(),
# #             "paid_members": [
# #                 {
# #                     "full_name": m.user.name,
# #                     "status": m.status,
# #                     "joined_at": m.joined_at
# #                 } for m in members.filter(id__in=paid_members)
# #             ],
# #             "unpaid_members": [
# #                 {
# #                     "full_name": m.user.name,
# #                     "status": m.status,
# #                     "joined_at": m.joined_at
# #                 } for m in unpaid_members
# #             ],
# #             "winners": [
# #                 {
# #                     "full_name": m.user.name,
# #                     "draw_date": LotteryWinner.objects.get(equb=equb, winner=m.user).draw_date
# #                 } for m in winners
# #             ],
# #             "unwinners": [
# #                 {
# #                     "full_name": m.user.name,
# #                 } for m in unwinners
# #             ]
# #         }

# #         return Response({"message": "Equb detailed report", "data": data}, status=status.HTTP_200_OK)

# #     except Equb.DoesNotExist:
# #         return Response({"message": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)

# #     except Exception as e:
# #         return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated,IsAdminUser])
# # def admin_equb_report(request):
# #     try:
# #         report = {
# #             "total_equbs": Equb.objects.count(),
# #             "total_equb_members": EqubMember.objects.count(),
# #             "total_equb_categories": EqubCategory.objects.count(),
# #             "total_equb_subcategories": EqubSubCategory.objects.count(),

# #             "equbs_per_category": Equb.objects.values('subcategory__category__name').annotate(total=Count('id')),
# #             "equbs_per_subcategory": Equb.objects.values('subcategory__name').annotate(total=Count('id')),

# #             "active_members": EqubMember.objects.filter(status='active').count(),
# #             "inactive_members": EqubMember.objects.filter(status='inactive').count(),

# #             "pending_payments": Payment.objects.filter(status='pending').count(),
# #             "completed_payments": Payment.objects.filter(status='completed').count(),
# #             "total_payment_amount": Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,

# #             "lottery_winners": LotteryWinner.objects.count(),
# #             "support_tickets_open": SupportTicket.objects.filter(status='open').count(),
# #             "support_tickets_resolved": SupportTicket.objects.filter(status='resolved').count(),
# #         }

# #         return Response({
# #             "message": "Admin report generated successfully",
# #             "data": report
# #         }, status=status.HTTP_200_OK)

# #     except Exception as e:
# #         return Response({
# #             "message": f"Failed to generate report: {str(e)}",
# #             "data": {}
# #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






# # @receiver(post_save, sender=LotteryWinner)
# # def notify_winner(sender, instance, created, **kwargs):
# #     if created:
# #         winner = instance.winner
# #         equb_name = instance.equb.name
# #         message = f"🎉 Congratulations! You have won the lottery for the Equb: {equb_name}."
        
# #         Notification.objects.create(
# #             user=winner,
# #             notif_type="Winner",
# #             message=message,
# #             created_at=timezone.now()
# #         )




# # @api_view(['GET'])
# # def customer_total_payment_for_equb(request, equb_id, user_id):
# #     try:
# #         equb = Equb.objects.get(id=equb_id)
# #     except Equb.DoesNotExist:
# #         return Response({"detail": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)

# #     try:
# #         user = User.objects.get(id=user_id)
# #     except User.DoesNotExist:
# #         return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# #     try:
# #         member = EqubMember.objects.get(equb=equb, user=user)
# #     except EqubMember.DoesNotExist:
# #         return Response({"detail": "User is not a member of the specified Equb."}, status=status.HTTP_404_NOT_FOUND)

# #     total_paid = Payment.objects.filter(equb_member=member, status='completed').aggregate(
# #         total=Sum('amount')
# #     )['total'] or 0.00

# #     return Response({
# #         "equb_id": str(equb.id),
# #         "equb_name": equb.name,
# #         "user_id": str(user.id),
# #         "email": user.email,
# #         "total_paid": total_paid
# #     })



# # @api_view(['GET'])
# # def customer_equb_contributions(request, user_id):
# #     try:
# #         user = User.objects.get(id=user_id)
# #     except User.DoesNotExist:
# #         return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

# #     contributions = []
# #     equb_memberships = EqubMember.objects.filter(user=user)

# #     for membership in equb_memberships:
# #         total_paid = Payment.objects.filter(
# #             equb_member=membership,
# #             status='completed'
# #         ).aggregate(total=Sum('amount'))['total'] or 0.00

# #         contributions.append({
# #             "equb_id": str(membership.equb.id),
# #             "equb_name": membership.equb.name,
# #             "total_paid": total_paid
# #         })

# #     return Response({
# #         "user_id": str(user.id),
# #         "email": user.email,
# #         "equb_contributions": contributions
# #     })



# # @api_view(['GET'])
# # @permission_classes([IsAdminUser])
# # def admin_view_equbs_with_members(request):
# #     equbs = Equb.objects.all()
# #     serializer = EqubSerializer(equbs, many=True)
# #     return Response(serializer.data)



# # @api_view(['POST'])
# # @permission_classes([IsAuthenticated])
# # def upload_receipt(request, equb_member_id):
# #     try:
# #         equb_member = EqubMember.objects.get(id=equb_member_id, user=request.user)
# #     except EqubMember.DoesNotExist:
# #         return Response({"error": "Equb member not found."}, status=status.HTTP_404_NOT_FOUND)

# #     receipt_image = request.FILES.get('recipt_image')
# #     if not receipt_image:
# #         return Response({"error": "Receipt image is required."}, status=status.HTTP_400_BAD_REQUEST)

# #     payment = Payment.objects.create(
# #         equb_member=equb_member,
# #         amount=request.data.get("amount"),
# #         payment_method=request.data.get("payment_method", "manual"),
# #         transaction_id=request.data.get("transaction_id"),
# #         recipt_image=receipt_image,
# #         status='pending'
# #     )

# #     return Response({"message": "Receipt uploaded successfully."}, status=status.HTTP_201_CREATED)


# # from datetime import timedelta
# # from django.utils import timezone
# # from rest_framework.decorators import api_view, permission_classes
# # from rest_framework.response import Response
# # from rest_framework import status
# # from .models import Equb

# # @api_view(['GET'])
# # @permission_classes([IsAuthenticated, IsCustomerUser])
# # def get_draw_countdown(request, equb_id):
# #     # Get the Equb object
# #     equb = get_object_or_404(Equb, id=equb_id)

# #     # Handle lottery_draw_schedule update logic based on EqubType
# #     equb_type = equb.subcategory.default_equb_type  # Assuming the `EqubSubCategory` links to `EqubType`
    
# #     if equb_type:
# #         if equb_type.name.lower() == 'daily':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(days=1)
# #         elif equb_type.name.lower() == 'weekly':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=1)
# #         elif equb_type.name.lower() == 'monthly':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=4)  # Approximation of a month
# #         elif equb_type.name.lower() == '2 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=8)  # Approximation of 2 months
# #         elif equb_type.name.lower() == '3 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=12)  # Approximation of 3 months
# #         elif equb_type.name.lower() == '6 months':
# #             next_draw_date = equb.lottery_draw_schedule + timedelta(weeks=24)  # Approximation of 6 months
# #         else:
# #             next_draw_date = equb.lottery_draw_schedule  # No change if type is unknown

# #         # Ensure the next draw is within the `end_date`
# #         if next_draw_date <= equb.end_date:
# #             # Calculate the countdown (time difference between now and the next draw)
# #             time_difference = next_draw_date - timezone.now()
# #             days_left = time_difference.days
# #             hours_left = time_difference.seconds // 3600
# #             minutes_left = (time_difference.seconds % 3600) // 60

# #             countdown = f"{days_left} days, {hours_left} hours, {minutes_left} minutes"
# #             next_draw_info = next_draw_date.strftime('%Y-%m-%d')  # Return as a date string
# #         else:
# #             next_draw_info = "Completed - No more draws"
# #             countdown = None  # No countdown if there are no more draws

# #     else:
# #         next_draw_info = "EqubType not found"
# #         countdown = None  # No countdown if EqubType is not found

# #     return Response({
# #         "next_draw_schedule": next_draw_info,
# #         "countdown": countdown  # Return the countdown
# #     }, status=status.HTTP_200_OK)
