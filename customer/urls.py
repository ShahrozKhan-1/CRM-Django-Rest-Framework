from django.urls import path
from .views import *

urlpatterns = [
    path("customer/", CustomerView.as_view()),
    path("customer/<int:customer_id>/", CustomerView.as_view()),
]