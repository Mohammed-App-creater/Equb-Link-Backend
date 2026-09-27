from django.urls import path
from user.views import *

urlpatterns = [
    path("signup", signup, name="signup"),
    path("login", login, name="login"),
    path("me/", me, name="me"),
    path("api/owner/login", loginWithToken, name="login_with_token"),
    path("api/owner/profile/", owner_profile, name="owner-profile"),
    path("signup/customer/", customer_signup),
    path("admin/create/", create_admin),
    path("equb-admin/create/", create_equb_admin),
    path("profile/update/", UpdateProfileView.as_view(), name="profile-update"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change-password"),
]
