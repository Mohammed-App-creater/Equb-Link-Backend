# =========================
# Python standard library
# =========================
import hashlib
import random
import secrets
import uuid

# =========================
# Third-party libraries
# =========================
import pandas as pd
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import AllowAny, SAFE_METHODS
from user.permissions import IsAdminUser
from equbApp.uploads import validate_image_upload
from django.core.exceptions import ValidationError as DjangoValidationError
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
from equbApp.models import Equb, EqubMember, EqubType, EqubCategory, LotteryWinner, OwnerBankAccount, Payment
from equbApp.serializers import EqubTypeSerializer, EqubCategorySerializer
from owner_panel.models import LotteryRound


class OwnerEqubListCreateView(generics.ListCreateAPIView):

    serializer_class = OwnerEqubSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return Equb.objects.filter(owner=self.request.user).prefetch_related(
            "payout_bank_accounts",
        ).order_by("-created_at")

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

        equb = get_object_or_404(Equb, 
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

        return equb.members.all().order_by("-joined_at")

class OwnerMemberApproveView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, member_id):

        member = get_object_or_404(EqubMember, 
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

        member = get_object_or_404(EqubMember, 
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

        equb = get_object_or_404(Equb, 
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

        qs = Payment.objects.filter(
            equb_member__equb=equb
        ).order_by("-created_at")

        status_param = self.request.GET.get("status")
        if status_param:
            qs = qs.filter(status=status_param)

        return qs

class OwnerPaymentApproveView(APIView):

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id, payment_id):

        payment = get_object_or_404(Payment, 
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

        payment = get_object_or_404(Payment, 
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

        equb = get_object_or_404(Equb, 
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
            status="active"
        )

        # All paid?
        for m in members:
            if not Payment.objects.filter(
                equb_member=m,
                status="completed",
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

        # Unpredictable before the draw (random seed), reproducible after it
        # from the recorded seed; the pool is sorted so the order is stable.
        seed = secrets.token_hex(16)
        pool.sort(key=lambda m: str(m.id))
        winner = random.Random(seed).choice(pool)

        round_obj, _ = LotteryRound.objects.get_or_create(
            equb=equb,
            round=round,
            defaults={"seed": seed}
        )

        round_obj.winner = winner.user
        round_obj.seed = seed
        round_obj.drawn_at = timezone.now()
        round_obj.save()

        LotteryWinner.objects.update_or_create(
            equb=equb,
            round_number=round,
            defaults={
                "winner": winner,
                "draw_date": timezone.now(),
            }
        )

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

        round_obj = get_object_or_404(LotteryRound, 
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

            def xlsx_safe(value):
                # Spreadsheet formula injection: neutralise cells that Excel
                # would evaluate (=, +, -, @, tab, CR).
                text = "" if value is None else str(value)
                return "'" + text if text[:1] in ("=", "+", "-", "@", "\t", "\r") else text

            data = [
                {
                    "member": xlsx_safe(p.equb_member.user.phone),
                    "amount": p.amount,
                    "status": xlsx_safe(p.status),
                    "round": p.round_number,
                    "approved_by": xlsx_safe(p.approved_by.phone if p.approved_by else ""),
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
    
class OwnerEqubTypeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsEqubOwner]
    serializer_class = EqubTypeSerializer
    queryset = EqubType.objects.all()


class IsEqubOwnerRole(IsEqubOwner):
    """Role check only — shared catalog objects have no owner to compare against."""

    def has_object_permission(self, request, view, obj):
        return True


class OwnerEqubTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EqubTypeSerializer
    queryset = EqubType.objects.all()

    def get_permissions(self):
        # Types are shared by every owner: read for owners, change/delete for
        # platform admins only.
        if self.request.method in SAFE_METHODS:
            return [IsEqubOwnerRole()]
        return [IsAdminUser()]


class OwnerEqubCategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsEqubOwner]
    serializer_class = EqubCategorySerializer
    queryset = EqubCategory.objects.all().order_by('-is_favorite', 'name')


class OwnerEqubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EqubCategorySerializer
    queryset = EqubCategory.objects.all()

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsEqubOwnerRole()]
        return [IsAdminUser()]


# =========================== Manual payment recording ===========================
from decimal import Decimal, InvalidOperation

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status as drf_status

from equbApp.models import Notification


class OwnerPaymentRecordView(APIView):
    """
    Owner records a contribution received outside the app (cash / bank /
    telebirr). Multipart body: equb_member, amount, round_number,
    payment_method, receipt_image (optional). Created as `completed`
    because the owner is confirming receipt.
    """

    permission_classes = [IsEqubOwner]

    def post(self, request, equb_id):
        equb = get_object_or_404(Equb, id=equb_id, owner=request.user)

        member_id = request.data.get("equb_member")
        raw_amount = request.data.get("amount")
        raw_round = request.data.get("round_number")
        payment_method = (request.data.get("payment_method") or "cash").strip().lower()

        if not member_id or raw_amount in (None, "") or raw_round in (None, ""):
            return Response(
                {"error": "equb_member, amount and round_number are required."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        try:
            amount = Decimal(str(raw_amount))
            round_number = int(raw_round)
        except (InvalidOperation, ValueError):
            return Response(
                {"error": "amount must be a number and round_number a whole number."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        if amount <= 0 or round_number < 1:
            return Response(
                {"error": "amount and round_number must be positive."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        try:
            member = EqubMember.objects.filter(id=member_id, equb=equb).first()
        except (ValueError, DjangoValidationError):
            member = None
        if member is None:
            return Response(
                {"error": "Member does not belong to this equb."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )
        if Payment.objects.filter(equb_member=member, round_number=round_number).exists():
            return Response(
                {"error": "A payment for this member and round already exists."},
                status=drf_status.HTTP_400_BAD_REQUEST,
            )

        receipt = request.FILES.get("receipt_image")
        try:
            validate_image_upload(receipt)
        except DjangoValidationError as exc:
            return Response({"error": " ".join(exc.messages)}, status=drf_status.HTTP_400_BAD_REQUEST)

        now = timezone.now()
        payment = Payment.objects.create(
            equb_member=member,
            amount=amount,
            payment_method=payment_method,
            transaction_id=f"MANUAL-{uuid.uuid4().hex[:10].upper()}",
            receipt_image=receipt,
            paid_at=now,
            status="completed",
            approved_by=request.user,
            approved_at=now,
            round_number=round_number,
        )

        AuditLog.objects.create(
            user=request.user,
            action="record_payment",
            target=str(payment.id),
            meta={
                "member": str(member.id),
                "round": round_number,
                "amount": str(amount),
                "method": payment_method,
            },
        )
        Notification.objects.create(
            user=member.user,
            notif_type="payment_approved",
            message=(
                f"Your {payment_method} payment of ETB {amount} for {equb.name} "
                f"(Round {round_number}) was recorded by the equb owner."
            ),
        )

        return Response(
            OwnerPaymentSerializer(payment).data,
            status=drf_status.HTTP_201_CREATED,
        )
