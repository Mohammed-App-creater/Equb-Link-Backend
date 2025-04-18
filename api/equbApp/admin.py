from django.contrib import admin
from .models import (
    EqubType, 
    EqubCategory, 
    EqubSubCategory, 
    Equb, 
    EqubMember, 
    Payment, 
    LotteryWinner, 
    Notification, 
    SupportTicket
)

@admin.register(EqubType)
class EqubTypeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(EqubCategory)
class EqubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']

@admin.register(EqubSubCategory)
class EqubSubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'default_equb_type']

@admin.register(Equb)
class EqubAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'owner', 'subcategory', 'start_date', 'end_date', 'payout_system']

@admin.register(EqubMember)
class EqubMemberAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'equb', 'status', 'payment_status', 'joined_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'equb_member', 'amount', 'status', 'paid_at']

@admin.register(LotteryWinner)
class LotteryWinnerAdmin(admin.ModelAdmin):
    list_display = ['id', 'equb', 'winner', 'draw_date']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'notif_type', 'is_read', 'created_at']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'subject', 'status', 'created_at']
