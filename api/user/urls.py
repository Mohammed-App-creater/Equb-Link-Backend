from django.urls import path
from user.views import *

urlpatterns = [
    path("signup", signup, name="signup"),
    path("login", login, name="login"),
    path("me/", me, name="me"),
    path("logout/", logout, name="logout"),
    path("api/owner/logout/", logout, name="owner-logout"),
    path("api/owner/login", loginWithToken, name="login_with_token"),
    path("api/owner/profile/", owner_profile, name="owner-profile"),
    path("signup/customer/", customer_signup),
    path("api/admin/create/", create_admin),
    path("equb-admin/create/", create_equb_admin),
    path("profile/update/", UpdateProfileView.as_view(), name="profile-update"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
    # Password reset via SMS code (mobile app); same views under /api/owner/ for the admin panel
    path("password-reset/request/", password_reset_request, name="password-reset-request"),
    path("password-reset/confirm/", password_reset_confirm, name="password-reset-confirm"),
    path("api/owner/password-reset/request/", password_reset_request, name="owner-password-reset-request"),
    path("api/owner/password-reset/confirm/", password_reset_confirm, name="owner-password-reset-confirm"),
]
