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

    # def validate_assigned_to(self, value):
    #     customer = value.get("customer")
    #     if customer:
    #         user = customer.assigned_to
    #         if user and user.roles.lower() != 'sales':
    #             raise ValidationError("Deal can only be assigned to sales representative")
    #         value["assigned_to"]=user
    #     return user
    
    # def validate(self, data):
    #     lead = data.get("lead")
    #     customer = data.get("customer")

    #     if lead and lead.customers != customer:
    #         raise ValidationError("Lead does not belong to the selected customer")
    #     return data
    def validate(self, attrs):
        assigned_to = attrs.get("assigned_to")
        customer = attrs.get("customer")
        lead = attrs.get("lead")
        if assigned_to and customer:
            if customer.assigned_to != assigned_to:
                raise ValidationError(
                    {"assigned_to": "Assigned user does not belong to this customer"}
                )
        if lead and customer:
            if lead.customers != customer:
                raise ValidationError(
                    {"lead": "Lead does not belong to the selected customer"}
                )

        return attrs
    

class LimitedDealSerializer(ModelSerializer):
    class Meta:
        model = Deal
        fields = ["title", "amount", "stage", "assigned_to" ]



class DealStageSerializer(ModelSerializer):
    class Meta:
        model = Deal
        fields = ["stage"]

    # def validate(self, value):
    #     transition = {
    #             "Open":["Won", "Lost"],
    #             "Won":["Close"]
    #         }
    #     current = self.instance.stage
    #     if value not in transition.get(current, []):
    #         raise ValidationError(f"Cannot change stage from {current} to {value}")
        # return value