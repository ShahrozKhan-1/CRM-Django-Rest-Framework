from django.urls import path
from .views import *


urlpatterns = [
    path("all-users/", CreateUser.as_view(), name="get all user"),
    path("create-user/", CreateUser.as_view(), name="create user"),
    path("edit-user/<int:user_id>/", CreateUser.as_view(), name="create user"),
    path("login/", LoginView.as_view(), name="login")
]