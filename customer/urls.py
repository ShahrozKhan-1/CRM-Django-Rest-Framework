from django.urls import path
from .views import *

urlpatterns = [
    path("customer/", CustomerView.as_view()),
    path("user-customer/", UserCustomerView.as_view()),
    path("edit-customer/<int:customer_id>/", UserCustomerView.as_view()),
]