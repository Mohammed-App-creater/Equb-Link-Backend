from django.urls import path
from . import views

urlpatterns = [

    # Equbs
    path("equbs/", views.OwnerEqubListCreateView.as_view()),
    
    path("equbs/<uuid:pk>/", views.OwnerEqubDetailView.as_view()),

    # Members
    path(
        "equbs/<uuid:equb_id>/members/",
        views.OwnerMemberListView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/members/<uuid:member_id>/approve/",
        views.OwnerMemberApproveView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/members/<uuid:member_id>/reject/",
        views.OwnerMemberRejectView.as_view()
    ),

    # Payments
    path(
        "equbs/<uuid:equb_id>/payments/",
        views.OwnerPaymentListView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/payments/<uuid:payment_id>/approve/",
        views.OwnerPaymentApproveView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/payments/<uuid:payment_id>/reject/",
        views.OwnerPaymentRejectView.as_view()
    ),

    # Dashboard
    path(
        "dashboard/",
        views.OwnerDashboardView.as_view()
    ),
    
    # Rounds
    path(
        "equbs/<uuid:equb_id>/rounds/",
        views.OwnerRoundListView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/rounds/<int:round>/draw/",
        views.OwnerDrawView.as_view()
    ),

    path(
        "equbs/<uuid:equb_id>/rounds/<int:round>/payout/",
        views.OwnerPayoutView.as_view()
    ),

    # Export
    path(
        "equbs/<uuid:equb_id>/export/",
        views.OwnerExportView.as_view()
    ),

]
