from django.urls import path
from .views import *


urlpatterns = [
    path("lead/", LeadView.as_view(), name="get create lead"),
    path("lead/<int:lead_id>/", LeadView.as_view(), name="get single and edit lead"),
    path("lead-status/<int:lead_id>/", LeadStatus.as_view(), name="change lead status")
]