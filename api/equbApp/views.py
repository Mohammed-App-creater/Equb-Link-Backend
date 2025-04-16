from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from user.permissions import IsAdminUser, IsCustomerUser
from .models import Equb, EqubCategory, EqubSubCategory, EqubType,EqubMember
from .serializers import (
    EqubSerializer,
    EqubCategorySerializer,
    EqubSubCategorySerializer,
    EqubTypeSerializer,
    EqubMemberSerializer,
    EqubSubCategoryPostSerializer,
    EqubPostSerializer,
    SubCategoryWithEqubsSerializer,
    EqubMemberPostSerializer,
    EqubMemberDataSerializer
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Sum
from .models import Equb, EqubMember, Payment, LotteryWinner, SupportTicket, EqubCategory, EqubSubCategory

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import LotteryWinner, Notification
from django.utils import timezone

# ---------------------- EqubType ----------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_type_list_create_admin(request):
    if request.method == "GET":
        types = EqubType.objects.all()
        serializer = EqubTypeSerializer(types, many=True)
        return Response(
            {"data": serializer.data, "message": "Get successfully"},
            status=status.HTTP_200_OK,
        )

    elif request.method == "POST":
        serializer = EqubTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
            return Response(
                {"data": serializer.data, "message": "Updated successfully"}
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif request.method == "DELETE":
        instance.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


# ---------------------- EqubCategory ----------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_category_list_create_admin(request):
    if request.method == "GET":
        categories = EqubCategory.objects.all()
        serializer = EqubCategorySerializer(categories, many=True)
        return Response({"data": serializer.data, "message": "Get successfully"})

    elif request.method == "POST":
        serializer = EqubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )


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
            return Response(
                {"data": serializer.data, "message": "Updated successfully"}
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif request.method == "DELETE":
        instance.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


# ---------------------- EqubSubCategory ----------------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_subcategory_list_create_admin(request):
    if request.method == "GET":
        subcategories = EqubSubCategory.objects.all()
        serializer = EqubSubCategorySerializer(subcategories, many=True)
        return Response({"data": serializer.data, "message": "Get successfully"})

    elif request.method == "POST":
        serializer = EqubSubCategoryPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PUT", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_subcategory_detail_admin(request, id):
    instance = get_object_or_404(EqubSubCategory, id=id)

    if request.method == "GET":
        serializer = EqubSubCategorySerializer(instance)
        return Response({"data": serializer.data, "message": "Get successfully"})

    elif request.method == "PUT":
        serializer = EqubSubCategorySerializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Updated successfully"}
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif request.method == "DELETE":
        instance.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


# ---------------------- Equb ----------------------

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_list_create_admin(request):
    if request.method == "GET":
        equbs = Equb.objects.all()
        serializer = EqubSerializer(equbs, many=True)
        return Response({"data": serializer.data, "message": "Get successfully"})

    elif request.method == "POST":
        data = request.data.copy()
        data["owner"] = str(request.user.id)  # set the owner to the logged-in user
        serializer = EqubPostSerializer(data=data)
        # serializer = EqubPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"data": serializer.data, "message": "Created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomerUser])
def equb_list_customer(request):
    equbs = Equb.objects.all()
    serializer = EqubSerializer(equbs, many=True)
    return Response({"data": serializer.data, "message": "Get successfully"})


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
            return Response(
                {"data": serializer.data, "message": "Updated successfully"}
            )
        return Response(
            {"data": serializer.errors, "message": "Error"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    elif request.method == "DELETE":
        instance.delete()
        return Response(
            {"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )
# To list all EqubSubCategory by EqubCategory ID, you can create a Django REST API endpoint like this:
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_subcategories_by_category(request, category_id):
    """
    List all EqubSubCategory by category ID
    """
    category = get_object_or_404(EqubCategory, id=category_id)
    subcategories = EqubSubCategory.objects.filter(category=category)
    serializer = EqubSubCategorySerializer(subcategories, many=True)
    return Response(
        {"data": serializer.data, "message": "Subcategories fetched successfully"},
        status=status.HTTP_200_OK
    )


from django.db.models import Count, Sum, Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EqubCategory, EqubSubCategory, Equb, Payment
from .serializers import SubCategoryWithEqubsSerializer, EqubSerializer

@api_view(['GET'])
def subcategories_with_equbs_by_category(request, category_id):
    try:
        subcategories = EqubSubCategory.objects.filter(category__id=category_id)

        if not subcategories.exists():
            return Response({
                "data": [],
                "message": "No subcategories found for this category."
            }, status=status.HTTP_404_NOT_FOUND)

        subcategory_data = []

        for subcat in subcategories:
            # Annotate each equb under this subcategory with total members and completed payment total
            equbs = Equb.objects.filter(subcategory=subcat).annotate(
                total_members=Count('equbmember', distinct=True),
                total_payout=Sum(
                    'equbmember__payment__amount',
                    filter=Q(equbmember__payment__status='completed'),
                    default=0
                )
            )

            subcat_serialized = SubCategoryWithEqubsSerializer(subcat)
            equb_serialized = EqubSerializer(equbs, many=True)

            subcategory_data.append({
                "id": subcat.id,
                "name": subcat.name,
                "description": subcat.description,
                "image": request.build_absolute_uri(subcat.image.url) if subcat.image else None,
                "equbs": equb_serialized.data
            })

        return Response({
            "data": subcategory_data,
            "message": "Fetched successfully"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "data": [],
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def equbs_by_subcategory(request, subcategory_id):
    try:
        equbs = Equb.objects.filter(subcategory__id=subcategory_id)
        serializer = EqubSerializer(equbs, many=True)
        return Response({
            "data": serializer.data,
            "message": "Equbs fetched successfully"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "error": str(e),
            "message": "An error occurred"
        }, status=status.HTTP_400_BAD_REQUEST)
    

#     Get all Equbs that the current authenticated user has joined.

@api_view(["GET"])
@permission_classes([IsAuthenticated,IsCustomerUser])
def equbs_user_joined(request):
    """
    Get all Equbs that the current authenticated user has joined.
    """
    equb_memberships = EqubMember.objects.filter(user=request.user)
    equbs = Equb.objects.filter(id__in=equb_memberships.values_list("equb_id", flat=True))
    serializer = EqubSerializer(equbs, many=True)
    return Response(
        {"data": serializer.data, "message": "Equbs joined by user retrieved successfully"},
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomerUser])
def join_equb(request):
    try:
        # Extract the user and equb ID from the request data
        user_id = request.data.get('user')
        equb_id = request.data.get('equb')

        print(f"Received user_id: {user_id}, equb_id: {equb_id}")
        
        # Fetch the user and equb instances
        user = User.objects.get(id=user_id)
        equb = Equb.objects.get(id=equb_id)

        print(f"Found user: {user}, equb: {equb}")

        # Check if the user is already a member of the Equb
        if EqubMember.objects.filter(user=user, equb=equb).exists():
            return Response({
                "message": "User is already a member of this Equb."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Create a new EqubMember instance
        new_member = EqubMember.objects.create(
            user=user,
            equb=equb,
            total_members=equb.total_number_of_members,
            status='active',
            payment_status='pending'
        )

        # Update the rules_and_condit_status to True
        equb.rules_and_condit_status = True
        equb.save()

        # Serialize the newly created member and return
        serializer = EqubMemberPostSerializer(new_member)
        return Response({
            "data": serializer.data,
            "message": "User successfully joined the Equb. Rules and conditions confirmed."
        }, status=status.HTTP_201_CREATED)

    except User.DoesNotExist:
        return Response({"message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    except Equb.DoesNotExist:
        return Response({"message": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"message": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Equb, EqubMember
from user.models import Customer
from .serializers import EqubMemberDataSerializer

@api_view(['GET'])
def equb_members(request, equb_id):
    try:
        # Fetch the Equb instance
        equb = Equb.objects.get(id=equb_id)

        # Fetch all members of the Equb
        members = EqubMember.objects.filter(equb=equb)

        # Create a list to hold serialized data
        response_data = []

        for member in members:
            # Fetch the corresponding Customer for each member
            customer = Customer.objects.get(user=member.user)
            
            # Serialize the member data and include customer name
            member_data = EqubMemberDataSerializer(member).data
            member_data['customer_name'] = customer.name  # Add customer name to the response data
            
            # Append to the response data list
            response_data.append(member_data)

        return Response({
            "data": response_data,
            "message": "Fetched Equb members successfully."
        }, status=status.HTTP_200_OK)

    except Equb.DoesNotExist:
        return Response({
            "message": "Equb not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({
            "message": "Customer not found for one of the members."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def unjoin_equb(request):
    try:
        # Extract the user and equb ID from the request data
        user_id = request.data.get('user')
        equb_id = request.data.get('equb')

        # Fetch the user and equb instances
        user = User.objects.get(id=user_id)
        equb = Equb.objects.get(id=equb_id)

        # Check if the user is a member of the Equb
        equb_member = EqubMember.objects.filter(user=user, equb=equb).first()
        if not equb_member:
            return Response({
                "message": "User is not a member of this Equb."
            }, status=status.HTTP_400_BAD_REQUEST)

        # Delete the EqubMember record to unjoin
        equb_member.delete()

        # Return success response
        return Response({
            "message": "User successfully unjoined the Equb."
        }, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({
            "message": "User not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Equb.DoesNotExist:
        return Response({
            "message": "Equb not found."
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            "message": f"An error occurred: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# list all members for each equb

@api_view(['GET'])
def list_equb_members(request, equb_id):
    members = EqubMember.objects.filter(equb_id=equb_id)
    serializer = EqubMemberSerializer(members, many=True)
    return Response({
        "data": serializer.data,
        "message": f"Members of Equb ID {equb_id} retrieved successfully"
    }, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import random

from .models import Equb, EqubMember, LotteryWinner
from user.models import Customer  # or the appropriate model for user info
from user.permissions import IsCustomerUser  # assuming you have this defined

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsCustomerUser])
def preview_equb_winner(request, equb_id):
    try:
        equb = Equb.objects.get(id=equb_id)
    except Equb.DoesNotExist:
        return Response({"error": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)

    # Get IDs of already selected winners
    winners = LotteryWinner.objects.filter(equb=equb).values_list('winner_id', flat=True)

    # Get eligible members who haven't won yet
    eligible_members = EqubMember.objects.filter(
        equb=equb,
        status='active'
    ).exclude(user_id__in=winners)

    if not eligible_members.exists():
        return Response({"message": "No eligible members left to win."}, status=status.HTTP_400_BAD_REQUEST)

    # Randomly select one eligible member
    selected_member = random.choice(list(eligible_members))
    try:
        customer = Customer.objects.get(user=selected_member.user)
        selected_name = customer.name
    except Customer.DoesNotExist:
        selected_name = selected_member.user.email  # fallback to email if name not found

    return Response({
        "message": f"{selected_name} is selected as a potential winner.",
        "winner": {
            "user_id": str(selected_member.user.id),
            "name": selected_name,
            "equb_id": str(equb.id),
        }
    }, status=status.HTTP_200_OK)



# save  winner after it spin 
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .models import Equb, LotteryWinner
from user.models import User, Customer  # your custom Account model is aliased as User
from user.permissions import IsCustomerUser


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsCustomerUser])
def confirm_and_save_winner(request):
    user_id = request.data.get('user')
    equb_id = request.data.get('equb')

    if not equb_id or not user_id:
        return Response({"error": "equb_id and user_id are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        equb = Equb.objects.get(id=equb_id)
        user = User.objects.get(id=user_id)
    except (Equb.DoesNotExist, User.DoesNotExist):
        return Response({"error": "Invalid equb or user ID."}, status=status.HTTP_404_NOT_FOUND)

    # Check if the user has already won
    already_won = LotteryWinner.objects.filter(equb=equb, winner=user).exists()
    if already_won:
        return Response({"message": "This user has already won before."}, status=status.HTTP_400_BAD_REQUEST)

    # Save the winner
    winner = LotteryWinner.objects.create(
        equb=equb,
        winner=user,
        draw_date=timezone.now()
    )

    # Try to get the name from the Customer model
    try:
        customer = Customer.objects.get(user=user)
        winner_name = customer.name
    except Customer.DoesNotExist:
        winner_name = user.email  # fallback to email if name not available

    return Response({
        "message": f"{winner_name} has been saved as the winner.",
        "draw_date": winner.draw_date
    }, status=status.HTTP_201_CREATED)



#     # Get all EqubMemberships for this user

from django.db.models import Sum
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EqubMember, Payment

# list total contirbute money by each equb  

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsCustomerUser])
def user_equb_payment_summary(request, user_id):
    # Get all EqubMemberships for this user
    memberships = EqubMember.objects.filter(user_id=user_id)

    if not memberships.exists():
        return Response({"message": "User is not a member of any Equb."}, status=status.HTTP_404_NOT_FOUND)

    # Prepare payment summary per Equb
    result = []
    for member in memberships:
        total_payment = Payment.objects.filter(equb_member=member, status='completed') \
                                       .aggregate(total=Sum('amount'))['total'] or 0
        
        result.append({
            "equb_id": str(member.equb.id),
            "equb_name": member.equb.name,
            "total_paid": float(total_payment),
        })

    return Response({
        "user_id": user_id,
        "payment_summary": result,
        "message": "Payment summary fetched successfully."
    }, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import EqubMember, Payment
from .serializers import PaymentSerializer  # Make sure this serializer exists


# list all the payement Hisotry of the user 

@api_view(['GET'])
@permission_classes([IsAuthenticated,IsCustomerUser])
def list_user_payment_history(request, user_id):
    # Get all EqubMember instances for the user
    equb_members = EqubMember.objects.filter(user_id=user_id)

    if not equb_members.exists():
        return Response({
            "message": "No Equb memberships found for this user."
        }, status=status.HTTP_404_NOT_FOUND)

    # Get all payments for these memberships
    payments = Payment.objects.filter(equb_member__in=equb_members).select_related('equb_member', 'equb_member__equb')

    # Optional: Order by most recent
    payments = payments.order_by('-paid_at')

    serializer = PaymentSerializer(payments, many=True)

    return Response({
        "user_id": user_id,
        "payment_history": serializer.data,
        "message": "User payment history retrieved successfully."
    }, status=status.HTTP_200_OK)


# admin report 

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def equb_detailed_report(request, equb_id):
    try:
        # Fetch the Equb object
        equb = Equb.objects.get(id=equb_id)

        # Fetch members associated with the Equb
        members = EqubMember.objects.filter(equb=equb)
        member_ids = members.values_list('id', flat=True)

        # Fetch paid members
        paid_members = Payment.objects.filter(equb_member__in=member_ids, status='completed').values_list('equb_member', flat=True).distinct()
        unpaid_members = members.exclude(id__in=paid_members)

        # Fetch winners
        winner_user_ids = LotteryWinner.objects.filter(equb=equb).values_list('winner_id', flat=True)
        winners = members.filter(user_id__in=winner_user_ids)
        unwinners = members.exclude(user_id__in=winner_user_ids)

        # Prepare the report data
        data = {
            "equb_name": equb.name,
            "total_members": members.count(),
            "paid_members_count": paid_members.count(),
            "unpaid_members_count": unpaid_members.count(),
            "winners_count": winners.count(),
            "unwinners_count": unwinners.count(),
            "paid_members": [
                {
                    "full_name": m.user.name,
                    "status": m.status,
                    "joined_at": m.joined_at
                } for m in members.filter(id__in=paid_members)
            ],
            "unpaid_members": [
                {
                    "full_name": m.user.name,
                    "status": m.status,
                    "joined_at": m.joined_at
                } for m in unpaid_members
            ],
            "winners": [
                {
                    "full_name": m.user.name,
                    "draw_date": LotteryWinner.objects.get(equb=equb, winner=m.user).draw_date
                } for m in winners
            ],
            "unwinners": [
                {
                    "full_name": m.user.name,
                } for m in unwinners
            ]
        }

        return Response({"message": "Equb detailed report", "data": data}, status=status.HTTP_200_OK)

    except Equb.DoesNotExist:
        return Response({"message": "Equb not found"}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['GET'])
@permission_classes([IsAuthenticated,IsAdminUser])
def admin_equb_report(request):
    try:
        report = {
            "total_equbs": Equb.objects.count(),
            "total_equb_members": EqubMember.objects.count(),
            "total_equb_categories": EqubCategory.objects.count(),
            "total_equb_subcategories": EqubSubCategory.objects.count(),

            "equbs_per_category": Equb.objects.values('subcategory__category__name').annotate(total=Count('id')),
            "equbs_per_subcategory": Equb.objects.values('subcategory__name').annotate(total=Count('id')),

            "active_members": EqubMember.objects.filter(status='active').count(),
            "inactive_members": EqubMember.objects.filter(status='inactive').count(),

            "pending_payments": Payment.objects.filter(status='pending').count(),
            "completed_payments": Payment.objects.filter(status='completed').count(),
            "total_payment_amount": Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0,

            "lottery_winners": LotteryWinner.objects.count(),
            "support_tickets_open": SupportTicket.objects.filter(status='open').count(),
            "support_tickets_resolved": SupportTicket.objects.filter(status='resolved').count(),
        }

        return Response({
            "message": "Admin report generated successfully",
            "data": report
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "message": f"Failed to generate report: {str(e)}",
            "data": {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)






@receiver(post_save, sender=LotteryWinner)
def notify_winner(sender, instance, created, **kwargs):
    if created:
        winner = instance.winner
        equb_name = instance.equb.name
        message = f"🎉 Congratulations! You have won the lottery for the Equb: {equb_name}."
        
        Notification.objects.create(
            user=winner,
            notif_type="Winner",
            message=message,
            created_at=timezone.now()
        )




@api_view(['GET'])
def customer_total_payment_for_equb(request, equb_id, user_id):
    try:
        equb = Equb.objects.get(id=equb_id)
    except Equb.DoesNotExist:
        return Response({"detail": "Equb not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    try:
        member = EqubMember.objects.get(equb=equb, user=user)
    except EqubMember.DoesNotExist:
        return Response({"detail": "User is not a member of the specified Equb."}, status=status.HTTP_404_NOT_FOUND)

    total_paid = Payment.objects.filter(equb_member=member, status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0.00

    return Response({
        "equb_id": str(equb.id),
        "equb_name": equb.name,
        "user_id": str(user.id),
        "email": user.email,
        "total_paid": total_paid
    })



@api_view(['GET'])
def customer_equb_contributions(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    contributions = []
    equb_memberships = EqubMember.objects.filter(user=user)

    for membership in equb_memberships:
        total_paid = Payment.objects.filter(
            equb_member=membership,
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0.00

        contributions.append({
            "equb_id": str(membership.equb.id),
            "equb_name": membership.equb.name,
            "total_paid": total_paid
        })

    return Response({
        "user_id": str(user.id),
        "email": user.email,
        "equb_contributions": contributions
    })



@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_view_equbs_with_members(request):
    equbs = Equb.objects.all()
    serializer = EqubSerializer(equbs, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_receipt(request, equb_member_id):
    try:
        equb_member = EqubMember.objects.get(id=equb_member_id, user=request.user)
    except EqubMember.DoesNotExist:
        return Response({"error": "Equb member not found."}, status=status.HTTP_404_NOT_FOUND)

    receipt_image = request.FILES.get('recipt_image')
    if not receipt_image:
        return Response({"error": "Receipt image is required."}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.create(
        equb_member=equb_member,
        amount=request.data.get("amount"),
        payment_method=request.data.get("payment_method", "manual"),
        transaction_id=request.data.get("transaction_id"),
        recipt_image=receipt_image,
        status='pending'
    )

    return Response({"message": "Receipt uploaded successfully."}, status=status.HTTP_201_CREATED)
