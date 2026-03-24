from django.db import models
from user_auth.models import User

# Create your models here.

class Lead(models.Model):

    class STATUS(models.TextChoices):
        NEW = 'New', 'new'
        CONTACTED = 'Contacted', 'contacted'
        QUALIFIED = 'Qualified', 'qualified'
        CONVERTED = 'Converted', 'converted'
        CLOSED_LOST = 'Closed_Lost', 'closed_lost'

    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    description = models.TextField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_lead")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="updated_lead", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, choices=STATUS.choices, default=STATUS.NEW)
    is_deleted = models.BooleanField(default=False)

    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="assigned_leads")



class LeadAttachments(models.Model):
    attachment = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    public_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    leads = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="lead_attachment")