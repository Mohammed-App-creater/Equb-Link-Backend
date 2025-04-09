from django.urls import path
from equbApp.views import *

urlpatterns = [
    # EqubType
    path(
        "admin_equb_types/",
        equb_type_list_create_admin,
        name="equb-type-list-create-admin",
    ),
    path(
        "admin_equb_types/<int:id>/",
        equb_type_detail_admin,
        name="equb-type-detail-admin",
    ),
    # EqubCategory
    path(
        "admin_equb_categories/",
        equb_category_list_create_admin,
        name="equb-category-list-create-admin",
    ),
    path(
        "admin_equb_categories/<int:id>/",
        equb_category_detail_admin,
        name="equb-category-detail-admin",
    ),
    # EqubSubCategory
    path(
        "admin_equb_subcategories/",
        equb_subcategory_list_create_admin,
        name="equb-subcategory-list-create-admin",
    ),
    path(
        "admin_equb_subcategories/<int:id>/",
        equb_subcategory_detail_admin,
        name="equb-subcategory-detail-admin",
    ),
    path(
        "equb_subcategories/by_category/<int:category_id>/",
        list_subcategories_by_category,
        name="equb-subcategories-by-category",
    ),

    # Equb
    path("admin_equbs/", equb_list_create_admin, name="equb-list-create-admin"),
    path("admin_equbs/<int:id>/", equb_detail_admin, name="equb-detail-admin"),
    path("customer_equbs/", equb_list_customer, name="equb-list-customer"),
    path("customer_equbs_joined/", equbs_user_joined, name="equbs-user-joined"),
    path('equb/<uuid:equb_id>/members/', list_equb_members, name='equb-members'),
    # equbs_by_subcategory
    path("equbs_by_subcategory/<uuid:subcategory_id>/", equbs_by_subcategory, name="equbs_by_subcategory-user-joined"),
    # subcategories_with_equbs_by_category
    path("subcategories_with_equbs_by_category/<uuid:category_id>/", subcategories_with_equbs_by_category, name="subcategories_with_equbs_by_category-user-joined"),

    path('join_equb/', join_equb, name='join_equb'),
    path('all_equb_members/<uuid:equb_id>/', equb_members, name='equb_members'),
    path('unjoin_equb/', unjoin_equb, name='unjoin_equb'),  # Add this line for unjoin functionality

    # notify_winner
    path('notify_winner/', notify_winner, name='notify_winner'),  

    # preview_equb_winner
    path('preview_equb_winner/<uuid:equb_id>/', preview_equb_winner, name='preview_equb_winner'),
    # confirm_and_save_winner
    path('confirm_and_save_winner/', confirm_and_save_winner, name='confirm_and_save_winner'),

    # admin_equb_report
    path('admin_equb_report/', admin_equb_report, name='admin_equb_report'),  
    path('equb_detailed_report/<uuid:equb_id>/', equb_detailed_report, name='equb_detailed_report'),  
    # "list_user_payment_history"
    path('list_user_payment_history/', list_user_payment_history, name='list_user_payment_history'),

    # user_equb_payment_summary
    path('user_equb_payment_summary/<int:user_id>/', user_equb_payment_summary, name='user_equb_payment_summary'),

]
