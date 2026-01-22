from django.urls import path
from .views import *


urlpatterns = [
    path("lead/", LeadView.as_view(), name="get create lead"),
    path("delete-lead/<int:lead_id>/", LeadView.as_view(), name="delete lead"),
    path("edit-lead/<int:lead_id>/", UserLeadView.as_view(), name="edit lead"),
    path("user-lead/", UserLeadView.as_view(), name="get user assigned lead"),
    path("lead-status/<int:lead_id>/", LeadStatus.as_view(), name="change lead status")
]