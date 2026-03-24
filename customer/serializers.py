from rest_framework.serializers import ModelSerializer, ValidationError, PrimaryKeyRelatedField
from .models import Customer
from lead.serializers import LeadSerializer
from user_auth.models import User


class CustomerSerializer(ModelSerializer):
    assigned_to = PrimaryKeyRelatedField(queryset=User.objects.all())
    lead = LeadSerializer(read_only=True)
    class Meta:
        model = Customer
        exclude = ["is_deleted"]

    

class LimitedCustomerSerailizer(ModelSerializer):
    class Meta:
        model = Customer
        fields = ["name", "company", "email", "phone", "assigned_to"]