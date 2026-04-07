from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Q
from .bank_constants import ETHIOPIAN_BANKS
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


# ===========================
# EQUbType Admin
# ===========================
@admin.register(EqubType)
class EqubTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


# ===========================
# EQUbCategory Admin (WITH TOTAL VALUE)
# ===========================
@admin.register(EqubCategory)
class EqubCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "total_equb_value",
        "image_preview",
    )
    search_fields = ("name",)
    readonly_fields = ("image_preview", "total_equb_value")

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"

    def total_equb_value(self, obj):
        total = obj.equbs.filter(status="active").aggregate(
            total=Sum("total_equb_value")
        )["total"]
        return total or 0

    total_equb_value.short_description = "Total Equb Value (Active)"


# ===========================
# EQUb Member Inline
# ===========================
class EqubMemberInline(admin.TabularInline):
    model = EqubMember
    extra = 0
    readonly_fields = (
        "joined_at",
        "has_received_payout",
        "payment_status",
    )
    fields = (
        "user",
        "status",
        "payment_status",
        "has_received_payout",
        "joined_at",
    )
    show_change_link = True


class EqubAdminForm(forms.ModelForm):
    class Meta:
        model = Equb
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        owner = cleaned_data.get("owner")
        accounts = cleaned_data.get("payout_bank_accounts")
        if owner and accounts is not None:
            for a in accounts:
                if a.owner_id != owner.id:
                    raise forms.ValidationError(
                        {
                            "payout_bank_accounts": (
                                "Every selected account must belong to the equb owner."
                            )
                        }
                    )
        return cleaned_data


class OwnerBankAccountAdminForm(forms.ModelForm):
    class Meta:
        model = OwnerBankAccount
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = [("", "---------")] + [
            (b["code"], f"{b['name']} ({b['code']})") for b in ETHIOPIAN_BANKS
        ]
        self.fields["bank_code"].widget = forms.Select(choices=choices)


# ===========================
# Owner bank accounts
# ===========================
@admin.register(OwnerBankAccount)
class OwnerBankAccountAdmin(admin.ModelAdmin):
    form = OwnerBankAccountAdminForm
    list_display = (
        "owner",
        "bank_code",
        "account_short",
        "account_holder_name",
        "label",
        "created_at",
    )
    list_filter = ("bank_code",)
    search_fields = (
        "account_number",
        "account_holder_name",
        "label",
        "owner__phone",
        "owner__email",
    )
    raw_id_fields = ("owner",)
    ordering = ("-created_at",)
    list_select_related = ("owner",)
    readonly_fields = ("created_at", "updated_at")

    @admin.display(description="Account #")
    def account_short(self, obj):
        n = obj.account_number
        if len(n) <= 6:
            return n
        return f"…{n[-4:]}"


# ===========================
# EQUb Admin
# ===========================
@admin.register(Equb)
class EqubAdmin(admin.ModelAdmin):
    form = EqubAdminForm
    filter_horizontal = ("payout_bank_accounts",)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "payout_bank_accounts":
            obj = kwargs.get("obj")
            if obj and getattr(obj, "owner_id", None):
                kwargs["queryset"] = OwnerBankAccount.objects.filter(
                    owner_id=obj.owner_id
                ).order_by("bank_code", "-created_at")
            else:
                kwargs["queryset"] = OwnerBankAccount.objects.none()
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    list_display = (
        "name",
        "owner",
        "category",
        "equb_type",
        "status",
        "payout_account_summary",
        "total_members",
        "contribution_amount",
        "total_payout",
        "total_equb_value",
        "payout_system",
        "start_date",
        "end_date",
    )

    list_filter = (
        "status",
        "category",
        "equb_type",
        "payout_system",
        "start_date",
        "end_date",
    )

    search_fields = (
        "name",
        "owner__phone",
        "owner__email",
        "owner__customer__name",
        "owner__equbadmin__name",
        "category__name",
        "equb_type__name",
    )

    readonly_fields = (
        "total_payout",
        "total_equb_value",
        "created_at",
        "updated_at",
    )

    inlines = [EqubMemberInline]

    fieldsets = (
        ("Basic Info", {
            "fields": ("name", "owner", "category", "equb_type")
        }),
        ("Financials", {
            "fields": (
                "total_members",
                "contribution_amount",
                "total_payout",
                "total_equb_value",
                "payout_system",
            )
        }),
        ("Payout bank accounts for this equb", {
            "fields": ("payout_bank_accounts",),
            "description": "Optional. Members can pay into any of these; all must belong to the owner.",
        }),
        ("Schedule & Rules", {
            "fields": (
                "start_date",
                "end_date",
                "lottery_draw_schedule",
                "rules",
                "rules_approved",
            )
        }),
        ("Status & Timestamps", {
            "fields": ("status", "created_at", "updated_at")
        }),
    )

    actions = ["approve_rules", "mark_completed"]

    @admin.display(description="Payout accounts")
    def payout_account_summary(self, obj):
        qs = list(obj.payout_bank_accounts.all()[:4])
        if not qs:
            return "—"
        parts = []
        for acc in qs:
            tail = acc.account_number[-4:] if len(acc.account_number) >= 4 else acc.account_number
            parts.append(f"{acc.bank_code} …{tail}")
        n = obj.payout_bank_accounts.count()
        if n > 4:
            parts.append(f"+{n - 4} more")
        return ", ".join(parts)

    def approve_rules(self, request, queryset):
        updated = queryset.update(rules_approved=True)
        self.message_user(request, f"{updated} Equbs rules approved.")

    approve_rules.short_description = "Approve rules for selected Equbs"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} Equbs marked as completed.")

    mark_completed.short_description = "Mark selected Equbs as completed"


# ===========================
# EqubMember Admin
# ===========================
@admin.register(EqubMember)
class EqubMemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "equb",
        "status",
        "payment_status",
        "has_received_payout",
        "joined_at",
    )
    search_fields = (
        "user__phone",
        "user__customer__name",
        "user__equbadmin__name",
        "equb__name",
    )
    list_filter = ("status", "payment_status", "has_received_payout")
    readonly_fields = ("joined_at", "updated_at")


# ===========================
# Payment Admin
# ===========================
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "equb_member",
        "amount",
        "round_number",
        "payment_method",
        "status",
        "paid_at",
        "receipt_preview",
    )
    search_fields = (
        "equb_member__user__name",
        "equb_member__equb__name",
        "transaction_id",
    )
    list_filter = ("status", "payment_method", "round_number")
    readonly_fields = ("receipt_preview", "created_at", "updated_at")

    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html('<img src="{}" width="50" />', obj.receipt_image.url)
        return "-"

    receipt_preview.short_description = "Receipt"


# ===========================
# Lottery Winner Admin
# ===========================
@admin.register(LotteryWinner)
class LotteryWinnerAdmin(admin.ModelAdmin):
    list_display = ("winner", "equb", "round_number", "draw_date")
    search_fields = ("winner__user__name", "equb__name")
    list_filter = ("round_number", "equb")


# ===========================
# Notification Admin
# ===========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notif_type", "is_read", "created_at")
    search_fields = ("user__name", "notif_type", "message")
    list_filter = ("notif_type", "is_read")


# ===========================
# SupportTicket Admin
# ===========================
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "created_at")
    search_fields = ("subject", "user__name", "message")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")
