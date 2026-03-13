from rest_framework.serializers import ModelSerializer, ValidationError, PrimaryKeyRelatedField
from .models import Lead
from user_auth.serializers import LimitedUserSerializer
from user_auth.models import User


class LeadSerializer(ModelSerializer):
    created_by = LimitedUserSerializer(read_only=True)
    updated_by = LimitedUserSerializer(read_only=True)
    assigned_to = PrimaryKeyRelatedField(queryset=User.objects.all())
    class Meta:
        model = Lead
        exclude = ["is_deleted"]

    
    def validate_assigned_to(self, user):
        if user and user.roles.lower() != 'sales':
            raise ValidationError("Lead can only be assigned to sales representative")
        return user
    

class LimitedLeadSerializer(ModelSerializer):
    class Meta:
        model = Lead
        fields = ["name", "email", "phone", "company", "status", "created_by"]
    


class LeadStatusSerializer(ModelSerializer):
    class Meta:
        model = Lead
        fields = ["status"]

    
    def validate(self, value):
        transition = {
            "New":["Contacted"],
            "Contacted":["Qualified", "Lost"],
            "Qualified":["Converted"],
            "Converted":["Closed_lost"]
        }
        current = self.instance.status
        allowed_status = transition.get(current, [])
        if value not in allowed_status:
            raise ValidationError(f"Cannot change status from {current} to {value}")
        return value