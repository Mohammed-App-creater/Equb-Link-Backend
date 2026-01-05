from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    EqubType,
    EqubCategory,
    EqubSubCategory,
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
    list_per_page = 25


# ===========================
# CATEGORY & SUBCATEGORY Admin
# ===========================
@admin.register(EqubCategory)
class EqubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "image_preview")
    search_fields = ("name",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"

    image_preview.short_description = "Image"


@admin.register(EqubSubCategory)
class EqubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "image_preview")
    search_fields = ("name", "category__name")
    list_filter = ("category",)
    readonly_fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" />', obj.image.url)
        return "-"

    image_preview.short_description = "Image"


# ===========================
# EQUb Member Inline
# ===========================
class EqubMemberInline(admin.TabularInline):
    model = EqubMember
    extra = 0
    readonly_fields = ("joined_at", "has_received_payout", "payment_status")
    show_change_link = True
    fields = ("user", "status", "payment_status", "has_received_payout", "joined_at")


# ===========================
# EQUb Admin
# ===========================
@admin.register(Equb)
class EqubAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "owner",
        "subcategory",
        "equb_type",
        "status",
        "total_members",
        "payment_per_round",
        "payout_system",
        "start_date",
        "end_date",
        "lottery_draw_schedule",
    )
    list_filter = (
        "status",
        "subcategory",
        "equb_type",
        "payout_system",
        "start_date",
        "end_date",
    )
    search_fields = (
        "name",
        "owner__full_name",
        "subcategory__name",
        "equb_type__name",
    )
    readonly_fields = ("created_at", "updated_at")
    inlines = [EqubMemberInline]

    fieldsets = (
        ("Basic Info", {"fields": ("name", "owner", "subcategory", "equb_type")}),
        (
            "Financial & Members",
            {"fields": ("total_members", "payment_per_round", "payout_system")},
        ),
        (
            "Schedule & Rules",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "lottery_draw_schedule",
                    "rules",
                    "rules_approved",
                )
            },
        ),
        ("Status & Timestamps", {"fields": ("status", "created_at", "updated_at")}),
    )

    actions = ["approve_rules", "mark_completed", "draw_lottery_winner"]

    # --- Custom actions ---
    def approve_rules(self, request, queryset):
        updated = queryset.update(rules_approved=True)
        self.message_user(request, f"{updated} Equbs rules approved.")

    approve_rules.short_description = "Approve rules for selected Equbs"

    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} Equbs marked as completed.")

    mark_completed.short_description = "Mark selected Equbs as completed"

    def draw_lottery_winner(self, request, queryset):
        from .utils import draw_lottery  # utility function

        for equb in queryset:
            winner = draw_lottery(equb)
            if winner:
                self.message_user(
                    request, f"Winner for {equb.name} is {winner.user.full_name}"
                )
            else:
                self.message_user(
                    request, f"No winner drawn for {equb.name} (check members/payment)"
                )

    draw_lottery_winner.short_description = "Draw lottery winner for selected Equbs"


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
        "updated_at",
    )
    search_fields = ("user__full_name", "equb__name")
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
        "created_at",
        "updated_at",
    )
    search_fields = (
        "equb_member__user__full_name",
        "equb_member__equb__name",
        "transaction_id",
    )
    list_filter = ("status", "payment_method", "round_number")
    readonly_fields = ("receipt_preview", "created_at", "updated_at")
    actions = ["mark_as_completed"]

    def receipt_preview(self, obj):
        if obj.receipt_image:
            return format_html('<img src="{}" width="50" />', obj.receipt_image.url)
        return "-"

    receipt_preview.short_description = "Receipt"

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"{updated} payments marked as completed.")

    mark_as_completed.short_description = "Mark selected payments as completed"


# ===========================
# Lottery Winner Admin
# ===========================
@admin.register(LotteryWinner)
class LotteryWinnerAdmin(admin.ModelAdmin):
    list_display = ("winner", "equb", "round_number", "draw_date")
    search_fields = ("winner__user__full_name", "equb__name")
    list_filter = ("round_number", "equb")


# ===========================
# Notification Admin
# ===========================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notif_type", "is_read", "created_at", "updated_at")
    search_fields = ("user__full_name", "notif_type", "message")
    list_filter = ("notif_type", "is_read")


# ===========================
# SupportTicket Admin
# ===========================
@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "status", "created_at", "updated_at")
    search_fields = ("subject", "user__full_name", "message")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at")
