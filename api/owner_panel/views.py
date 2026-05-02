# =========================
# Python standard library
# =========================
import hashlib
import random
import uuid

# =========================
# Third-party libraries
# =========================
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

# =========================
# Local app imports
# =========================
from .models import AuditLog
from .permissions import IsEqubOwner
from .serializers import (
    OwnerBankAccountSerializer,
    OwnerEqubSerializer,
    OwnerMemberSerializer,
    OwnerPaymentSerializer,
    OwnerRoundSerializer,
)

from equbApp.bank_constants import ETHIOPIAN_BANKS
from equbApp.models import Equb, EqubMember, EqubType, EqubCategory, OwnerBankAccount, Payment
from owner_panel.models import LotteryRound


class OwnerEqubListCreateView(generics.ListCreateAPIView):

    serializer_class = OwnerEqubSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return Equb.objects.filter(owner=self.request.user).prefetch_related(
            "payout_bank_accounts",
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OwnerEqubDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = OwnerEqubSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return Equb.objects.filter(owner=self.request.user).prefetch_related(
            "payout_bank_accounts",
        )

    def destroy(self, request, *args, **kwargs):

        equb = self.get_object()

        if Payment.objects.filter(
            equb_member__equb=equb
        ).exists():

            return Response(
                {"error": "Payments exist"},
                status=400
            )

        return super().destroy(request, *args, **kwargs)


class EthiopianBankListView(APIView):
    """List predefined banks / wallets (code, name, logo_url) for owner payout setup."""

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"banks": ETHIOPIAN_BANKS})


class OwnerBankAccountListCreateView(generics.ListCreateAPIView):
    """List or create bank accounts for the logged-in equb owner (multiple allowed)."""

    serializer_class = OwnerBankAccountSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return OwnerBankAccount.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class OwnerBankAccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete one of the owner's bank accounts."""

    serializer_class = OwnerBankAccountSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return OwnerBankAccount.objects.filter(owner=self.request.user)


class OwnerEqubBankingView(APIView):
    """
    Owner screen for one equb: selected payout account + all saved accounts.
    Each account includes linked_equbs (equbs that use it as payout).
    """

    permission_classes = [IsEqubOwner]

    def get(self, request, equb_id):
        equb = get_object_or_404(
            Equb.objects.prefetch_related("payout_bank_accounts"),
            id=equb_id,
            owner=request.user,
        )
        accounts = OwnerBankAccount.objects.filter(owner=request.user).order_by(
            "-created_at"
        )
        ser_ctx = {"request": request}
        return Response(
            {
                "equb_id": str(equb.id),
                "equb_name": equb.name,
                "payout_bank_accounts": OwnerBankAccountSerializer(
                    equb.payout_bank_accounts.all(), many=True, context=ser_ctx
                ).data,
                "owner_bank_accounts": OwnerBankAccountSerializer(
                    accounts, many=True, context=ser_ctx
                ).data,
            }
        )


class OwnerMemberListView(generics.ListAPIView):

    serializer_class = OwnerMemberSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):

        equb = Equb.objects.get(
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

        return equb.members.all()

class OwnerMemberApproveView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, member_id):

        member = EqubMember.objects.get(
            id=member_id,
            equb__id=equb_id,
            equb__owner=request.user
        )

        member.status = "active"
        member.save()

        AuditLog.objects.create(
            user=request.user,
            action="approve_member",
            target=str(member.id),
            meta={}
        )

        return Response({"status": "approved"})

class OwnerMemberRejectView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, member_id):

        member = EqubMember.objects.get(
            id=member_id,
            equb__id=equb_id,
            equb__owner=request.user
        )

        member.status = "removed"
        member.save()

        AuditLog.objects.create(
            user=request.user,
            action="reject_member",
            target=str(member.id),
            meta=request.data
        )

        return Response({"status": "rejected"})

class OwnerPaymentListView(generics.ListAPIView):

    serializer_class = OwnerPaymentSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):

        equb = Equb.objects.get(
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

        qs = Payment.objects.filter(
            equb_member__equb=equb
        )

        status_param = self.request.GET.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs

class OwnerPaymentApproveView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, payment_id):

        payment = Payment.objects.get(
            id=payment_id,
            equb_member__equb__id=equb_id,
            equb_member__equb__owner=request.user
        )

        payment.status = "completed"
        payment.approved_by = request.user
        payment.approved_at = timezone.now()
        payment.save()

        AuditLog.objects.create(
            user=request.user,
            action="approve_payment",
            target=str(payment.id),
            meta={}
        )

        return Response({"status": "completed"})

class OwnerPaymentRejectView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, payment_id):

        payment = Payment.objects.get(
            id=payment_id,
            equb_member__equb__id=equb_id,
            equb_member__equb__owner=request.user
        )

        payment.status = "rejected"
        payment.rejected_reason = request.data.get("reason")
        payment.save()

        AuditLog.objects.create(
            user=request.user,
            action="reject_payment",
            target=str(payment.id),
            meta=request.data
        )

        return Response({"status": "rejected"})

class OwnerDashboardView(APIView):
    permission_classes = [IsEqubOwner]

    def get(self, request):
        # Queryset of all Equbs owned by this user
        equbs = Equb.objects.filter(owner=request.user)

        pending_members = EqubMember.objects.filter(
            equb__owner=request.user,
            status="pending"
        ).count()

        pending_payments = Payment.objects.filter(
            equb_member__equb__owner=request.user,
            status="pending"
        ).count()

        return Response({
            "total_equbs": equbs.count(),
            "pending_members": pending_members,
            "pending_payments": pending_payments,
        })
class OwnerRoundListView(generics.ListAPIView):
    
    serializer_class = OwnerRoundSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        equb = get_object_or_404(
            Equb,
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

        # 1️⃣ Check for pending round
        pending_exists = LotteryRound.objects.filter(
            equb=equb,
            drawn_at__isnull=True
        ).exists()

        # 2️⃣ If none, create next round
        if not pending_exists:
            last_round = LotteryRound.objects.filter(
                equb=equb
            ).order_by("-round").first()

            next_round_number = 1 if not last_round else last_round.round + 1

            LotteryRound.objects.create(
                equb=equb,
                round=next_round_number,
                seed=uuid.uuid4().hex
            )

        # 3️⃣ Return all rounds
        return LotteryRound.objects.filter(
            equb=equb
        ).order_by("round")
class OwnerDrawView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, round):

        equb = Equb.objects.get(
            id=equb_id,
            owner=request.user,
            status="active"
        )

        # Already drawn?
        if LotteryRound.objects.filter(
            equb=equb,
            round=round,
            winner__isnull=False
        ).exists():

            return Response(
                {"error": "Already drawn"},
                status=400
            )

        members = EqubMember.objects.filter(
            equb=equb,
            status="approved"
        )

        # All paid?
        for m in members:
            if not Payment.objects.filter(
                equb_member=m,
                status="approved",
                round_number=round
            ).exists():
                return Response(
                    {"error": "Not all members paid"},
                    status=400
                )

        pool = list(
            members.exclude(
                has_received_payout=True
            )
        )

        if not pool:
            return Response(
                {"error": "No eligible members"},
                status=400
            )

        seed = hashlib.sha256(
            f"{equb.id}{round}".encode()
        ).hexdigest()

        random.seed(seed)

        winner = random.choice(pool)

        round_obj, _ = LotteryRound.objects.get_or_create(
            equb=equb,
            round=round
        )

        round_obj.winner = winner.user
        round_obj.seed = seed
        round_obj.drawn_at = timezone.now()
        round_obj.save()

        winner.has_received_payout = True
        winner.save()

        AuditLog.objects.create(
            user=request.user,
            action="draw_lottery",
            target=f"{equb.id}-R{round}",
            meta={"winner": str(winner.user.id)}
        )

        return Response({
            "winner_id": winner.user.id,
            "method": "random",
            "seed": seed
        })

class OwnerPayoutView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, round):

        round_obj = LotteryRound.objects.get(
            equb__id=equb_id,
            equb__owner=request.user,
            round=round
        )

        if not round_obj.winner:
            return Response(
                {"error": "No winner yet"},
                status=400
            )

        round_obj.is_paid = True
        round_obj.save()

        AuditLog.objects.create(
            user=request.user,
            action="mark_payout",
            target=str(round_obj.id),
            meta={}
        )

        return Response({"status": "paid"})

class OwnerExportView(APIView):
    permission_classes = [IsEqubOwner]

    def get(self, request, equb_id):
        equb = get_object_or_404(
            Equb,
            id=equb_id,
            owner=request.user
        )

        report_type = request.GET.get("type")

        if report_type == "payments":
            qs = Payment.objects.filter(
                equb_member__equb=equb
            )

            data = [
                {
                    "member": p.equb_member.user.phone,
                    "amount": p.amount,
                    "status": p.status,
                    "round": p.round_number,
                    "approved_by": p.approved_by.phone if p.approved_by else "",
                }
                for p in qs
            ]

            df = pd.DataFrame(data)

            response = HttpResponse(
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = "attachment; filename=payments.xlsx"

            df.to_excel(response, index=False)
            return response

        return Response({"error": "Invalid type"}, status=400)

class EqubReportSummaryView(APIView):
    permission_classes = [IsEqubOwner] # optionally, you can add IsEqubOwner permission

    def get(self, request, equb_id):
        # Fetch the Equb, ensure user is the owner
        equb = get_object_or_404(Equb, id=equb_id, owner=request.user)

        # Total members
        total_members = equb.total_members

        # Expected amount (from your model)
        expected_amount = float(equb.total_equb_value)

        # Payments for the last round
        last_round_number = Payment.objects.filter(
            equb_member__equb=equb
        ).order_by('-round_number').values_list('round_number', flat=True).first()

        # Collected amount (completed payments only)
        if last_round_number:
            completed_payments = Payment.objects.filter(
                equb_member__equb=equb,
                round_number=last_round_number,
                status="completed"
            )
            collected_amount = float(sum(p.amount for p in completed_payments))
            members_paid = completed_payments.values('equb_member').distinct().count()
        else:
            collected_amount = 0
            members_paid = 0

        pending_amount = expected_amount - collected_amount

        data = {
            "expectedAmount": expected_amount,
            "collectedAmount": collected_amount,
            "pendingAmount": pending_amount,
            "membersPaid": members_paid,
            "totalMembers": total_members,
        }

        return Response(data)

class EqubActivityView(APIView):
    permission_classes = [IsEqubOwner]  # Only Equb owner can see activity

    def get(self, request, equb_id):
        # Ensure user owns the Equb
        equb = get_object_or_404(Equb, id=equb_id, owner=request.user)

        # Get all users who belong to this Equb (members + owner)
        equb_user_ids = list(equb.members.values_list('user_id', flat=True)) + [request.user.id]

        # Fetch AuditLogs related to this Equb
        logs = AuditLog.objects.filter(user_id__in=equb_user_ids).order_by('-timestamp')

        # Map AuditLog to frontend ActivityLog structure
        activity_logs = []
        for log in logs:
            activity_logs.append({
                "id": str(log.id),
                "type": log.action,  # assuming action matches one of your frontend types
                "performedBy": log.user.phone,  # or log.user.username
                "entityName": log.target,
                "timestamp": log.timestamp.isoformat(),
                "metadata": str(log.meta) if log.meta else None,
            })

        return Response(activity_logs)
    
class EqubTypesView(generics.ListAPIView):
    permission_classes = [IsEqubOwner]
    
    def get(self, request):
        equb_types = EqubType.objects.all()
        data = [
            {
                "id": et.id,
                "name": et.name,
                "description": et.description,
            }
            for et in equb_types
        ]
        return Response(data)
    
class EqubCategoriesView(generics.ListAPIView):
    permission_classes = [IsEqubOwner]
    
    def get(self, request):
        equb_categories = EqubCategory.objects.all()
        data = [
            {
                "id": ec.id,
                "name": ec.name,
                "description": ec.description,
                "image": request.build_absolute_uri(ec.image.url) if ec.image else None,
            }
            for ec in equb_categories
        ]
        return Response(data)