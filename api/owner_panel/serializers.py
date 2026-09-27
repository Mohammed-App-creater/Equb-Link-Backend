from rest_framework import serializers
from equbApp.media_views import signed_media_url
from equbApp.models import (
    Equb,
    EqubMember,
    OwnerBankAccount,
    Payment,
    LotteryWinner,
    EqubType,
    EqubCategory,
)
from equbApp.serializers import EqubTypeSerializer, EqubCategorySerializer
from equbApp.bank_constants import get_bank_by_code, is_valid_bank_code
from owner_panel.models import LotteryRound


class OwnerBankAccountSerializer(serializers.ModelSerializer):
    bank_name = serializers.SerializerMethodField()
    bank_logo_url = serializers.SerializerMethodField()
    linked_equbs = serializers.SerializerMethodField()

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
            "linked_equbs",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_bank_name(self, obj):
        b = get_bank_by_code(obj.bank_code)
        return b["name"] if b else None

    def get_bank_logo_url(self, obj):
        b = get_bank_by_code(obj.bank_code)
        if not b:
            return None
        url = b.get("logo_url") or ""
        return url if url else None

    def get_linked_equbs(self, obj):
        """Equbs owned by this user that use this account as payout (may be empty)."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return []
        return list(
            Equb.objects.filter(
                owner_id=request.user.id,
                payout_bank_accounts=obj,
            ).values("id", "name")
        )

    def validate_bank_code(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError("Bank code is required.")
        if not is_valid_bank_code(value):
            raise serializers.ValidationError("Unknown bank or wallet code.")
        return str(value).upper().strip()

    def validate(self, attrs):
        acct = attrs.get("account_number", getattr(self.instance, "account_number", None))
        holder = attrs.get("account_holder_name", getattr(self.instance, "account_holder_name", None))
        if not acct or not str(acct).strip():
            raise serializers.ValidationError({"account_number": "This field is required."})
        if not holder or not str(holder).strip():
            raise serializers.ValidationError({"account_holder_name": "This field is required."})
        attrs["account_number"] = str(acct).strip()
        attrs["account_holder_name"] = str(holder).strip()
        if "label" in attrs and attrs["label"] is not None:
            attrs["label"] = str(attrs["label"]).strip()
        return attrs


class OwnerEqubSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    pending_members = serializers.SerializerMethodField()
    pending_payments = serializers.SerializerMethodField()

    # WRITE (input)
    category = serializers.PrimaryKeyRelatedField(
        queryset=EqubCategory.objects.all(),
        write_only=True
    )
    equb_type = serializers.PrimaryKeyRelatedField(
        queryset=EqubType.objects.all(),
        required=False,
        allow_null=True,
        write_only=True
    )

    # READ (output)
    category_detail = EqubCategorySerializer(source="category", read_only=True)
    equb_type_detail = EqubTypeSerializer(source="equb_type", read_only=True)

    payout_bank_accounts = OwnerBankAccountSerializer(many=True, read_only=True)
    payout_bank_account_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of OwnerBankAccount UUIDs for this equb (all must belong to you). Omit to leave unchanged on PATCH.",
    )

    class Meta:
        model = Equb
        exclude = ["owner"]

    def create(self, validated_data):
        ids = validated_data.pop("payout_bank_account_ids", None)
        instance = super().create(validated_data)
        if ids is not None:
            self._sync_payout_accounts(instance, ids)
        return instance

    def update(self, instance, validated_data):
        ids = validated_data.pop("payout_bank_account_ids", serializers.empty)
        instance = super().update(instance, validated_data)
        if ids is not serializers.empty:
            self._sync_payout_accounts(instance, ids)
        return instance

    def _sync_payout_accounts(self, instance, ids):
        if not ids:
            instance.payout_bank_accounts.clear()
            return
        unique_ids = list({str(u) for u in ids})
        qs = OwnerBankAccount.objects.filter(id__in=unique_ids, owner_id=instance.owner_id)
        if qs.count() != len(unique_ids):
            raise serializers.ValidationError(
                {
                    "payout_bank_account_ids": (
                        "One or more accounts are invalid or do not belong to this equb's owner."
                    )
                }
            )
        instance.payout_bank_accounts.set(qs)

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["receipt_image"] = signed_media_url(self.context.get("request"), instance.receipt_image)
        return data

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
