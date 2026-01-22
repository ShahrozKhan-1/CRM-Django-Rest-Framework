from django.urls import path
from .views import *


urlpatterns = [
    path("deal/", DealView.as_view()),
    path("deal/<int:deal_id>/", DealView.as_view()),
    path("user-deal/", UserDealView.as_view()),
    path("user-deal/<int:deal_id>/", UserDealView.as_view()),
    path("deal-status/<int:deal_id>/", DealStatus.as_view()),
]