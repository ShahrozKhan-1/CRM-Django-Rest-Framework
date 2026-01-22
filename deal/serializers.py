from rest_framework.serializers import ModelSerializer, ValidationError, PrimaryKeyRelatedField
from .models import Deal
from lead.models import Lead
from customer.models import Customer
from user_auth.models import User


class DealSerializer(ModelSerializer):
    lead = PrimaryKeyRelatedField(queryset=Lead.objects.all(), required=False, allow_null=True)
    customer = PrimaryKeyRelatedField(queryset=Customer.objects.all())
    assigned_to = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False, allow_null=True)
    class Meta:
        model = Deal
        exclude = ["is_deleted"]

    def validate_assigned_to(self, value):
        customer = value.get("customer")
        if customer:
            user = customer.assigned_to
            if user and user.roles.lower() != 'sales':
                raise ValidationError("Deal can only be assigned to sales representative")
            value["assigned_to"]=user
        return user
    
    def validate(self, data):
        lead = data.get("lead")
        customer = data.get("customer")

        if lead and lead.customers != customer:
            raise ValidationError("Lead does not belong to the selected customer")
        return data



class DealStageSerializer(ModelSerializer):
    class Meta:
        model = Deal
        fields = ["stage"]

    def validate(self, value):
        transition = {
                "Open":["Won", "Lost"],
                "Won":["Close"]
            }
        current = self.instance.stage
        if value not in transition.get(current, []):
            raise ValidationError(f"Cannot change stage from {current} to {value}")
        return value