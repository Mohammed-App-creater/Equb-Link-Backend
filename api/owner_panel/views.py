from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from equbApp.models import Equb, EqubMember, Payment
from .serializers import (
    OwnerEqubSerializer,
    OwnerMemberSerializer,
    OwnerPaymentSerializer,
    OwnerRoundSerializer
)
from .permissions import IsEqubOwner
from .models import AuditLog

import random
import hashlib

from owner_panel.models import LotteryRound

import pandas as pd
from django.http import HttpResponse




class OwnerEqubListCreateView(generics.ListCreateAPIView):

    serializer_class = OwnerEqubSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return Equb.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class OwnerEqubDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = OwnerEqubSerializer
    permission_classes = [IsEqubOwner]

    def get_queryset(self):
        return Equb.objects.filter(owner=self.request.user)

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

        member.status = "approved"
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

        member.status = "rejected"
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

        payment.status = "approved"
        payment.approved_by = request.user
        payment.approved_at = timezone.now()
        payment.save()

        AuditLog.objects.create(
            user=request.user,
            action="approve_payment",
            target=str(payment.id),
            meta={}
        )

        return Response({"status": "approved"})

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

        equb = Equb.objects.get(
            id=self.kwargs["equb_id"],
            owner=self.request.user
        )

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

        equb = Equb.objects.get(
            id=equb_id,
            owner=request.user
        )

        report_type = request.GET.get("type")

        if report_type == "payments":

            qs = Payment.objects.filter(
                equb_member__equb=equb
            )

            data = []

            for p in qs:
                data.append({
                    "member": p.equb_member.user.phone,
                    "amount": p.amount,
                    "status": p.status,
                    "round": p.round_number,
                    "approved_by": (
                        p.approved_by.phone
                        if p.approved_by else ""
                    ),
                })

            df = pd.DataFrame(data)

            response = HttpResponse(
                content_type="application/vnd.ms-excel"
            )

            response[
                "Content-Disposition"
            ] = "attachment; filename=payments.xlsx"

            df.to_excel(response, index=False)

            return response

        return Response(
            {"error": "Invalid type"},
            status=400
        )
