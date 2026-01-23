from django.urls import path
from .views import *
from .dashboard import DashboardView


urlpatterns = [
    path("all-users/", CreateUser.as_view(), name="get all user"),
    path("create-user/", CreateUser.as_view(), name="create user"),
    path("edit-user/<int:user_id>/", CreateUser.as_view(), name="create user"),
    path("login/", LoginView.as_view(), name="login"),

    path("search/", SearchAPIView.as_view(), name="search query"),

    path("dashboard/", DashboardView.as_view(), name="dashboard")
]