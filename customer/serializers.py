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

    def validate_assigned_to(self, user):
        if user and user.roles.lower() != 'sales':
            raise ValidationError("Lead can only be assigned to sales representative")
        return user