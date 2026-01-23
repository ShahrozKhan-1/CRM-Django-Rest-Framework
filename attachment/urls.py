from django.urls import path
from .views import *


urlpatterns = [
    path('customer-attachments/', CustomerAttachment.as_view()),
    path('customer-attachments/<int:customer_id>/', CustomerAttachment.as_view()),
    
    path('lead-attachments/', LeadAttachment.as_view()),
    path('lead-attachments/<int:lead_id>/', LeadAttachment.as_view()),
    
    path('deal-attachments/', DealAttachment.as_view()),
    path('deal-attachments/<int:deal_id>/', DealAttachment.as_view()),
]