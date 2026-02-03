from rest_framework import serializers
from equbApp.models import (
    Equb, EqubMember, Payment, LotteryWinner 
)
from equbApp.serializers import EqubTypeSerializer, EqubCategorySerializer
from owner_panel.models import LotteryRound


class OwnerEqubSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    pending_members = serializers.SerializerMethodField()
    pending_payments = serializers.SerializerMethodField()

    equb_type = EqubTypeSerializer(read_only=True)
    category = EqubCategorySerializer(read_only=True)

    class Meta:
        model = Equb
        exclude = ["owner"]

    def get_members(self, obj):
        return obj.members.count()

    def get_pending_members(self, obj):
        return obj.members.filter(status="pending").count()

    def get_pending_payments(self, obj):
        return Payment.objects.filter(
            equb_member__equb=obj,
            status="pending"
        ).count()

class OwnerMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    phone = serializers.CharField(source="user.phone", read_only=True)
    joined_at = serializers.DateTimeField(read_only=True)
    has_paid = serializers.SerializerMethodField()

    class Meta:
        model = EqubMember
        fields = [
            "id",
            "user_name",
            "phone",
            "status",
            "joined_at",
            "has_paid",
        ]

    def get_user_name(self, obj):
        user = obj.user

        # Customer
        if hasattr(user, "customer"):
            return user.customer.name

        # Equb Admin
        if hasattr(user, "equbadmin"):
            return user.equbadmin.name

        # System/Admin
        if hasattr(user, "admin"):
            return user.admin.name

        # Fallback
        return user.phone

    def get_has_paid(self, obj):
        return obj.payment_status == "paid"

class OwnerPaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = [
            "status",
            "approved_by",
            "approved_at"
        ]

class OwnerRoundSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    roundNumber = serializers.IntegerField(source="round")
    drawDate = serializers.DateTimeField(source="drawn_at", read_only=True)
    winnerName = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = LotteryRound
        fields = [
            "id",
            "roundNumber",
            "status",
            "winnerName",
            "drawDate",
            "is_paid",
        ]

    def get_status(self, obj):
        return "completed" if obj.drawn_at else "pending"

    def get_winnerName(self, obj):
        if not obj.winner:
            return None

        user = obj.winner
        if hasattr(user, "customer"):
            return user.customer.name
        elif hasattr(user, "equbadmin"):
            return user.equbadmin.name
        elif hasattr(user, "admin"):
            return user.admin.name

        return user.phone
