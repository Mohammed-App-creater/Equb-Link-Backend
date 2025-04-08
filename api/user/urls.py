from django.urls import path
from user.views import *

urlpatterns = [
    path("signup", signup, name="signup"),
    path("login", login, name="login"),
]
