# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ----------------- EqubType -----------------
    path(
        "api/admin/equb-types/",
        views.equb_type_list_create_admin,
        name="equb-type-list-create",
    ),
    path(
        "api/admin/equb-types/<uuid:id>/",
        views.equb_type_detail_admin,
        name="equb-type-detail",
    ),
    # ----------------- EqubCategory -----------------
    path(
        "api/admin/equb-categories/",
        views.equb_category_list_create_admin,
        name="equb-category-list-create",
    ),
    path(
        "api/admin/equb-categories/<uuid:id>/",
        views.equb_category_detail_admin,
        name="equb-category-detail",
    ),
    # ----------------- Equb -----------------
    path("api/admin/equbs/", views.equb_list_create_admin, name="equb-list-create"),
    path("api/admin/equbs/<uuid:id>/", views.equb_detail_admin, name="admin-equb-detail"),
    # ----------------- EqubMember -----------------
    path(
        "api/admin/equb-members/",
        views.equb_member_list_create_admin,
        name="equb-member-list-create",
    ),
    path(
        "api/admin/equb-members/<uuid:id>/",
        views.equb_member_detail_admin,
        name="equb-member-detail",
    ),
    # ----------------- Payment -----------------
    path(
        "api/admin/payments/", views.payment_list_create_admin, name="payment-list-create"
    ),
    path(
        "api/admin/payments/<uuid:id>/", views.payment_detail_admin, name="payment-detail"
    ),
    # ----------------- LotteryWinner -----------------
    path(
        "api/admin/lottery-winners/",
        views.lottery_winner_list_create_admin,
        name="lottery-winner-list-create",
    ),
    path(
        "api/admin/lottery-winners/<uuid:id>/",
        views.lottery_winner_detail_admin,
        name="lottery-winner-detail",
    ),
    # ----------------- Notification -----------------
    path(
        "api/admin/notifications/",
        views.notification_list_create_admin,
        name="notification-list-create",
    ),
    path(
        "api/admin/notifications/<uuid:id>/",
        views.notification_detail_admin,
        name="notification-detail",
    ),
    # ----------------- SupportTicket -----------------
    path(
        "api/admin/support-tickets/",
        views.support_ticket_list_create_admin,
        name="support-ticket-list-create",
    ),
    path(
        "api/admin/support-tickets/<uuid:id>/",
        views.support_ticket_detail_admin,
        name="support-ticket-detail",
    ),
    
    # Mobile API endpoint
    #     # ==================== Mobile API endpoint ====================

    path(
        "mobile_equb_categories/",
        views.equb_categories_with_count,
        name="mobile-equb-categories",
    ),
    
    path(
        "mobile_equbs_by_category/",
        views.get_active_equbs_by_category,
        name="mobile-equbs-by-category",
    ),
    
    # get_active_equbs_by_category_id
    
   path(
        "all_equb_by_category_id/<uuid:category_id>/",
        views.get_active_equbs_by_category_id,
        name="active-equbs-by-category",
    ),
   
    # List all active Equbs by EqubType ID
    path(
        "all_equb_by_equbs_type/<uuid:equb_type_id>/",
        views.get_active_equbs_by_type_id,
        name="active-equbs-by-type",
    ),
  
    
    path (
        "equb_join_cost/<uuid:equb_id>/",
        views.equb_join_cost,
        name="equb_join_cost"
    ),
    
# ===========================
    # EQUb PUBLIC / CUSTOMER APIs
    # ===========================

    # Join an Equb (accept terms + payment)
    path(
        "equbs/<uuid:equb_id>/join/",
        views.join_equb,
        name="join-equb"
    ),

    # Join an Equb before it starts (Round 0)
    path(
        "equbs/<uuid:equb_id>/join-initial/",
        views.join_equb_initial,
        name="join-equb-initial"
    ),

    # Join an Equb and pay via Chapa
    path(
        "equbs/<uuid:equb_id>/join-chapa/",
        views.join_equb_chapa,
        name="join-equb-chapa"
    ),
# ===========================
    # CUSTOMER DASHBOARD APIs
    # ===========================

    # Get single Equb detail (authenticated)
    path(
        "equbs/<uuid:id>/",
        views.equb_detail,
        name="equb-detail"
    ),

    # Customer Dashboard
    path(
        "customer/dashboard/",
        views.customer_dashboard,
        name="customer-dashboard"
    ),

    # Regular Round Payment
    path(
        "equbs/<uuid:equb_id>/pay/",
        views.pay_equb_contribution,
        name="pay-equb-contribution"
    ),

    # Pay contribution via Chapa (dedicated endpoint)
    path(
        "equbs/<uuid:equb_id>/pay-contribution-chapa/",
        views.pay_equb_contribution_chapa,
        name="pay-equb-contribution-chapa"
    ),
    
    # Chapa callback for contribution payments
    path("payment-success/", views.payment_success, name="payment-success"),

    # Admin Approve Payment
    path(
        "api/admin/payments/<uuid:payment_id>/approve/",
        views.admin_approve_payment,
        name="admin-approve-payment"
    ),
    
    
    path(
        "payment/pending-list/",
        views.list_pending_payments,
        name="List-pending-payment"
    ),

       
    
    # ----------------- Notifications (Customer) -----------------
    path("notifications/", views.customer_notifications, name="customer-notifications"),
    
    path("api/owner/notifications/", views.customer_notifications, name="owner-customer-notifications"),
    
    path("notifications/read/", views.mark_notification_as_read, name="mark-notifications-read"),
    
    path("api/owner/notifications/read/", views.mark_notification_as_read, name="owner-mark-notifications-read"),
    
    
    # ----------------- Chapa Pament -----------------
    
     # Initialize payment (React Native calls this)
    path("chapa/initialize/", views.initialize_chapa_payment, name="chapa-initialize"),

    # Verify payment
    path("chapa/verify/<str:tx_ref>/", views.verify_chapa_payment, name="chapa-verify"),

    # Chapa callback (Chapa calls this)
    path("chapa/callback/", views.chapa_callback, name="chapa-callback"),

    # ----------------- Notifications: bulk actions + pin (customer) -----------------
    path("notifications/read-all/", views.mark_all_notifications_as_read, name="mark-all-notifications-read"),
    path("notifications/clear-all/", views.clear_all_notifications, name="clear-all-notifications"),
    path("notifications/<uuid:notification_id>/toggle-pin/", views.toggle_notification_pin, name="toggle-notification-pin"),

    # ----------------- Support tickets (customer) -----------------
    path("support/tickets/", views.customer_support_tickets, name="customer-support-tickets"),
    
]
















