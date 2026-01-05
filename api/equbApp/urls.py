from django.urls import path
from equbApp.views import *

urlpatterns = [
    # ==================== EqubType ====================
    path(
        "admin_equb_types/",
        equb_type_list_create_admin,
        name="equb-type-list-create-admin",
    ),
    path(
        "admin_equb_types/<uuid:id>/",
        equb_type_detail_admin,
        name="equb-type-detail-admin",
    ),
    # ==================== EqubCategory ====================
    path(
        "admin_equb_categories/",
        equb_category_list_create_admin,
        name="equb-category-list-create-admin",
    ),
    path(
        "admin_equb_categories/<uuid:id>/",
        equb_category_detail_admin,
        name="equb-category-detail-admin",
    ),
    # ==================== EqubSubCategory ====================
    path(
        "admin_equb_subcategories/",
        equb_subcategory_list_create_admin,
        name="equb-subcategory-list-create-admin",
    ),
    path(
        "admin_equb_subcategories/<uuid:id>/",
        equb_subcategory_detail_admin,
        name="equb-subcategory-detail-admin",
    ),
    path(
        "equb_subcategories/by_category/<uuid:category_id>/",
        list_subcategories_by_category,
        name="equb-subcategories-by-category",
    ),
    # ==================== Equb ====================
    path("admin_equbs/", equb_list_create_admin, name="equb-list-create-admin"),
    path("admin_equbs/<uuid:id>/", equb_detail_admin, name="equb-detail-admin"),
    path("customer_equbs/", equb_list_customer, name="equb-list-customer"),
    path("customer_equbs_joined/", equbs_user_joined, name="equbs-user-joined"),
    # Equb filtering and related
    path(
        "equbs_by_subcategory/<uuid:subcategory_id>/",
        equbs_by_subcategory,
        name="equbs_by_subcategory",
    ),
    path(
        "subcategories_with_equbs_by_category/<uuid:category_id>/",
        subcategories_with_equbs_by_category,
        name="subcategories_with_equbs_by_category",
    ),
    # ==================== Equb Members ====================
    path("equb/<uuid:equb_id>/members/", list_equb_members, name="equb-members"),
    path("all_equb_members/<uuid:equb_id>/", equb_members, name="equb_members"),
    # Member actions
    path("join_equb/", join_equb, name="join_equb"),
    path("unjoin_equb/", unjoin_equb, name="unjoin_equb"),
    # ==================== Lottery & Winners ====================
    path(
        "preview_equb_winner/<uuid:equb_id>/",
        preview_equb_winner,
        name="preview_equb_winner",
    ),
    path(
        "confirm_and_save_winner/",
        confirm_and_save_winner,
        name="confirm_and_save_winner",
    ),
    # ==================== Payments ====================
    path(
        "list_user_payment_history/<str:user_id>/",
        list_user_payment_history,
        name="list_user_payment_history",
    ),
    path(
        "user_equb_payment_summary/<str:user_id>/",
        user_equb_payment_summary,
        name="user_equb_payment_summary",
    ),
    path(
        "upload_receipt/<uuid:equb_member_id>/", upload_receipt, name="upload_receipt"
    ),
    # ==================== Reports ====================
    path("admin_equb_report/", admin_equb_report, name="admin_equb_report"),
    path(
        "equb_detailed_report/<uuid:equb_id>/",
        equb_detailed_report,
        name="equb_detailed_report",
    ),
    path(
        "admin_view_equbs_with_members/",
        admin_view_equbs_with_members,
        name="admin_view_equbs_with_members",
    ),
    # ==================== Customer Payment Analytics ====================
    path(
        "equbs_users_total_paid/<uuid:equb_id>/<str:user_id>/",
        customer_total_payment_for_equb,
        name="customer_total_payment_for_equb",
    ),
    path(
        "users_equb_contributions/<str:user_id>/",
        customer_equb_contributions,
        name="customer_equb_contributions",
    ),
    # ==================== Utility ====================
    path(
        "get_draw_countdown/<uuid:equb_id>/",
        get_draw_countdown,
        name="get_draw_countdown",
    ),
]
# from django.urls import path
# from equbApp.views import *

# urlpatterns = [
#     # EqubType
#     path(
#         "admin_equb_types/",
#         equb_type_list_create_admin,
#         name="equb-type-list-create-admin",
#     ),
#     path(
#         "admin_equb_types/<uuid:id>/",
#         equb_type_detail_admin,
#         name="equb-type-detail-admin",
#     ),
#     # EqubCategory
#     path(
#         "admin_equb_categories/",
#         equb_category_list_create_admin,
#         name="equb-category-list-create-admin",
#     ),
#     path(
#         "admin_equb_categories/<uuid:id>/",
#         equb_category_detail_admin,
#         name="equb-category-detail-admin",
#     ),
#     # EqubSubCategory
#     path(
#         "admin_equb_subcategories/",
#         equb_subcategory_list_create_admin,
#         name="equb-subcategory-list-create-admin",
#     ),
#     path(
#         "admin_equb_subcategories/<uuid:id>/",
#         equb_subcategory_detail_admin,
#         name="equb-subcategory-detail-admin",
#     ),
#     path(
#         "equb_subcategories/by_category/<uuid:category_id>/",
#         list_subcategories_by_category,
#         name="equb-subcategories-by-category",
#     ),

#     # Equb
#     path("admin_equbs/", equb_list_create_admin, name="equb-list-create-admin"),
#     path("admin_equbs/<uuid:id>/", equb_detail_admin, name="equb-detail-admin"),
#     path("customer_equbs/", equb_list_customer, name="equb-list-customer"),
#     path("customer_equbs_joined/", equbs_user_joined, name="equbs-user-joined"),
#     path('equb/<uuid:equb_id>/members/', list_equb_members, name='equb-members'),
#     # equbs_by_subcategory
#     path("equbs_by_subcategory/<uuid:subcategory_id>/", equbs_by_subcategory, name="equbs_by_subcategory-user-joined"),
#     # subcategories_with_equbs_by_category
#     path("subcategories_with_equbs_by_category/<uuid:category_id>/", subcategories_with_equbs_by_category, name="subcategories_with_equbs_by_category-user-joined"),

#     path('join_equb/', join_equb, name='join_equb'),
#     path('all_equb_members/<uuid:equb_id>/', equb_members, name='equb_members'),
#     path('unjoin_equb/', unjoin_equb, name='unjoin_equb'),  # Add this line for unjoin functionality

#     # notify_winner
#     path('notify_winner/', notify_winner, name='notify_winner'),

#     # preview_equb_winner
#     path('preview_equb_winner/<uuid:equb_id>/', preview_equb_winner, name='preview_equb_winner'),
#     # confirm_and_save_winner
#     path('confirm_and_save_winner/', confirm_and_save_winner, name='confirm_and_save_winner'),

#     # admin_equb_report
#     path('admin_equb_report/', admin_equb_report, name='admin_equb_report'),
#     path('equb_detailed_report/<uuid:equb_id>/', equb_detailed_report, name='equb_detailed_report'),
#     # "list_user_payment_history"
#     path('list_user_payment_history/', list_user_payment_history, name='list_user_payment_history'),

#     # user_equb_payment_summary
#     path('user_equb_payment_summary/<int:user_id>/', user_equb_payment_summary, name='user_equb_payment_summary'),

#     path('equbs_users_total_paid/<uuid:equb_id>/<int:user_id>/', customer_total_payment_for_equb),
#     path('users_equb_contributions/<int:user_id>/', customer_equb_contributions),
#     # admin_view_equbs_with_members
#     path('admin_view_equbs_with_members/', admin_view_equbs_with_members, name='admin_view_equbs_with_members'),
#     # upload_receipt
#     path('upload_receipt/', upload_receipt, name='upload_receipt'),
#     # get_draw_countdown
#     path('get_draw_countdown/<uuid:equb_id>/', get_draw_countdown, name='get_draw_countdown'),
# ]
