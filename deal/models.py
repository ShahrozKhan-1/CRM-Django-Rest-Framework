from django.db import models
from customer.models import Customer
from user_auth.models import User
from lead.models import Lead
# Create your models here.


class Deal(models.Model):

    class STATUS(models.TextChoices):
        OPEN = "Open", "open"
        WON = "Won", "won"
        LOST = "Lost", "lost"
        CLOSED = "Closed", "closed"

    title = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    stage = models.CharField(max_length=255, choices=STATUS.choices, default=STATUS.OPEN)
    description = models.TextField(null=True)
    expected_close_date = models.DateField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updates_at = models.DateTimeField(auto_now=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name="deals", null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="deals")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deals")

    is_deleted = models.BooleanField(default=False)



class DealAttachments(models.Model):
    attachment = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    public_id = models.CharField(max_length=255)
    deals = models.ForeignKey(Deal, on_delete=models.CASCADE, related_name="deal_attachment")
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)