from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Q
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


# ===========================
# EQUb Admin
# ===========================
@admin.register(Equb)
class EqubAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "category",
        "equb_type",
        "status",
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
        "owner__name",
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
    search_fields = ("user__name", "equb__name")
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
