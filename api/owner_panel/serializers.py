from rest_framework import serializers
from equbApp.models import (
    Equb, EqubMember, Payment, 
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

    user_name = serializers.CharField(
        source="user.name",
        read_only=True
    )

    phone = serializers.CharField(
        source="user.phone",
        read_only=True
    )

    has_paid = serializers.SerializerMethodField()

    class Meta:
        model = EqubMember
        fields = [
            "id",
            "full_name",
            "user_name",
            "phone",
            "status",
            "has_paid"
        ]

    def get_has_paid(self, obj):
        return obj.payments.filter(status="approved").exists()

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

    winner_id = serializers.UUIDField(
        source="winner.id",
        read_only=True
    )

    class Meta:
        model = LotteryRound
        fields = [
            "round",
            "winner_id",
            "is_paid",
            "drawn_at"
        ]