from django.urls import path
from user.views import *

urlpatterns = [
    path("signup", signup, name="signup"),
    path("login", login, name="login"),
    path("api/owner/login", login, name="login"),
    path("signup/customer/", customer_signup),
    path("admin/create/", create_admin),
    path("equb-admin/create/", create_equb_admin),
]
