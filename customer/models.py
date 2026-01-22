from django.db import models
from user_auth.models import User
from lead.models import Lead

# Create your models here.

class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255)
    phone = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    assigned_to = models.ForeignKey(User, related_name="generated_customers", on_delete=models.CASCADE)
    lead = models.ForeignKey(Lead, related_name="customers", on_delete=models.CASCADE, null=True, blank=True)

    is_deleted = models.BooleanField(default=False)