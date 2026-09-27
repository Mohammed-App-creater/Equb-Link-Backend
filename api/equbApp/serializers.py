from django.contrib.auth import get_user_model
# serializers.py
from rest_framework import serializers
from .bank_constants import get_bank_by_code
from .models import (
    EqubType,
    EqubCategory,
    Equb,
    EqubMember,
    OwnerBankAccount,
    Payment,
    LotteryWinner,
    Notification,
    SupportTicket,
)

User = get_user_model()


# -------------------- EqubType --------------------
class EqubTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubType
        fields = "__all__"

# -------------------- EqubCategory --------------------
class EqubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubCategory
        fields = "__all__"

class EqubCategoryWithCountSerializer(serializers.ModelSerializer):
    total_equbs = serializers.SerializerMethodField()

    class Meta:
        model = EqubCategory
        fields = ["id", "name", "image", "description", "is_favorite","total_equbs"]

    def get_total_equbs(self, obj):
        return obj.equbs.count()  # 'equbs' is the related_name from Equb.category
# -------------------- Owner bank (public detail for members) --------------------
class OwnerBankAccountPublicSerializer(serializers.ModelSerializer):
    bank_name = serializers.SerializerMethodField()
    bank_logo_url = serializers.SerializerMethodField()

    class Meta:
        model = OwnerBankAccount
        fields = [
            "id",
            "bank_code",
            "bank_name",
            "bank_logo_url",
            "account_number",
            "account_holder_name",
            "label",
        ]

    def get_bank_name(self, obj):
        b = get_bank_by_code(obj.bank_code)
        return b["name"] if b else None

    def get_bank_logo_url(self, obj):
        b = get_bank_by_code(obj.bank_code)
        if not b:
            return None
        url = b.get("logo_url") or ""
        return url if url else None


# -------------------- Equb --------------------
class EqubSerializer(serializers.ModelSerializer):
    payout_bank_accounts = OwnerBankAccountPublicSerializer(many=True, read_only=True)

    class Meta:
        model = Equb
        fields = "__all__"

# -------------------- EqubMember --------------------

class UserPublicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "phone", "name")

    def get_name(self, obj):
        return (
            getattr(getattr(obj, "customer", None), "name", None)
            or getattr(getattr(obj, "equbadmin", None), "name", None)
            or getattr(getattr(obj, "admin", None), "name", None)
        )
class EqubMemberSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = EqubMember
        fields = (
            "user",
            "joined_at",
            "status",
        )

class EqubMemberCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EqubMember
        fields = ("user", "equb")

    def validate(self, data):
        equb = data["equb"]
        user = data["user"]

        if equb.members.count() >= equb.total_members:
            raise serializers.ValidationError("Equb member limit reached.")

        if EqubMember.objects.filter(user=user, equb=equb).exists():
            raise serializers.ValidationError("User is already a member of this Equb.")

        return data


# -------------------- Payment --------------------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

    def validate(self, data):
        equb_member = data.get("equb_member")
        round_number = data.get("round_number")
        amount = data.get("amount")

        # Duplicate payment for same round
        if Payment.objects.filter(equb_member=equb_member, round_number=round_number).exists():
            raise serializers.ValidationError(f"Payment for round {round_number} already exists.")

        # Amount check
        if amount != equb_member.equb.contribution_amount:
            raise serializers.ValidationError(f"Payment amount must match Equb contribution: {equb_member.equb.contribution_amount}")

        return data

# -------------------- LotteryWinner --------------------
class LotteryWinnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = LotteryWinner
        fields = "__all__"

    def validate(self, data):
        equb = data.get("equb")
        round_number = data.get("round_number")

        # Duplicate winner
        if LotteryWinner.objects.filter(equb=equb, round_number=round_number).exists():
            raise serializers.ValidationError(f"Winner already selected for round {round_number} of this Equb.")
        return data

# -------------------- Notification --------------------
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"

# -------------------- SupportTicket --------------------
class SupportTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportTicket
        fields = "__all__"

# -------------------- Join Equb Serializer --------------------
class JoinEqubSerializer(serializers.Serializer):
    equb_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_method = serializers.CharField(max_length=50)
    transaction_id = serializers.CharField(max_length=100)
    receipt_image = serializers.ImageField()

    def validate(self, data):
        user = self.context['request'].user
        equb_id = data.get('equb_id')
        equb = Equb.objects.get(id=equb_id)

        # Check if user is already a member
        if EqubMember.objects.filter(user=user, equb=equb).exists():
            raise serializers.ValidationError("You have already joined this Equb.")

        # Check contribution amount
        if data['amount'] != equb.contribution_amount * equb.total_members:
            raise serializers.ValidationError(
                f"You must pay the full amount until the current round: {equb.contribution_amount * equb.total_members}"
            )

        return data


# -------------------- Customer Support Ticket --------------------
class CustomerSupportTicketSerializer(serializers.ModelSerializer):
    """Customer-facing: the user is taken from the request, status is read-only."""
    class Meta:
        model = SupportTicket
        fields = ["id", "subject", "message", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]
