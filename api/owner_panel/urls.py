from django.urls import path
from . import views

urlpatterns = [

    # Banks / wallets (picker list)
    path(
        "banks/",
        views.EthiopianBankListView.as_view(),
        name="owner-banks-list",
    ),

    path(
        "bank-accounts/",
        views.OwnerBankAccountListCreateView.as_view(),
        name="owner-bank-accounts-list-create",
    ),
    path(
        "bank-accounts/<uuid:pk>/",
        views.OwnerBankAccountDetailView.as_view(),
        name="owner-bank-account-detail",
    ),

    # Equbs
    path("equbs/", views.OwnerEqubListCreateView.as_view(), name="owner-equb-list-create"),

    path(
        "equbs/<uuid:equb_id>/banking/",
        views.OwnerEqubBankingView.as_view(),
        name="owner-equb-banking",
    ),
    
    path("equbs/<uuid:pk>/", views.OwnerEqubDetailView.as_view(), name="owner-equb-detail"),

    # Members
    path(
        "equbs/<uuid:equb_id>/members/",
        views.OwnerMemberListView.as_view(),
        name="owner-member-list"
    ),

    path(
        "equbs/<uuid:equb_id>/members/<uuid:member_id>/approve/",
        views.OwnerMemberApproveView.as_view(),
        name="owner-member-approve"
    ),

    path(
        "equbs/<uuid:equb_id>/members/<uuid:member_id>/reject/",
        views.OwnerMemberRejectView.as_view(),
        name="owner-member-reject"
    ),

    # Payments
    path(
        "equbs/<uuid:equb_id>/payments/",
        views.OwnerPaymentListView.as_view(),
        name="owner-payment-list"
    ),

    path(
        "equbs/<uuid:equb_id>/payments/<uuid:payment_id>/approve/",
        views.OwnerPaymentApproveView.as_view(),
        name="owner-payment-approve"
    ),

    path(
        "equbs/<uuid:equb_id>/payments/<uuid:payment_id>/reject/",
        views.OwnerPaymentRejectView.as_view(),
        name="owner-payment-reject"
    ),

    # Dashboard
    path(
        "dashboard/",
        views.OwnerDashboardView.as_view(),
        name="owner-dashboard"
    ),
    
    # Rounds
    path(
        "equbs/<uuid:equb_id>/rounds/",
        views.OwnerRoundListView.as_view(),
        name="owner-round-list"
    ),

    path(
        "equbs/<uuid:equb_id>/rounds/<int:round>/draw/",
        views.OwnerDrawView.as_view(),
        name="owner-round-draw"
    ),

    path(
        "equbs/<uuid:equb_id>/rounds/<int:round>/payout/",
        views.OwnerPayoutView.as_view(),
        name="owner-round-payout"
    ),

    # Export
    path(
        "equbs/<uuid:equb_id>/export/",
        views.OwnerExportView.as_view(),
        name="owner-equb-export"
    ),
    
    path(
        'equbs/<uuid:equb_id>/reports/',
        views.EqubReportSummaryView.as_view(),
        name='equb-report-summary'
    ),
    
    # Activity Logs

    path(
        'equbs/<uuid:equb_id>/activity/',
        views.EqubActivityView.as_view(),
        name='equb-activity'
    ),
    
    # Equb Types
    path(
        'equbs/types/',
        views.OwnerEqubTypeListCreateView.as_view(),
        name='owner-equb-type-list'
    ),
    path(
        'equbs/types/<uuid:pk>/',
        views.OwnerEqubTypeDetailView.as_view(),
        name='owner-equb-type-detail'
    ),

    # Equb Categories
    path(
        'equbs/categories/',
        views.OwnerEqubCategoryListCreateView.as_view(),
        name='owner-equb-category-list'
    ),
    path(
        'equbs/categories/<uuid:pk>/',
        views.OwnerEqubCategoryDetailView.as_view(),
        name='owner-equb-category-detail'
    ),

]
