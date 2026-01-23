from rest_framework.serializers import ModelSerializer
from .models import Attachment
from lead.serializers import LimitedLeadSerializer
from deal.serializers import LimitedDealSerializer
from customer.serializers import LimitedCustomerSerailizer
from customer.models import Customer
from lead.models import Lead
from deal.models import Deal


from rest_framework import serializers

class AttachmentSerializer(serializers.ModelSerializer):
    attached_to = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        exclude = ["is_deleted"]

    def get_attached_to(self, instance):
        obj = instance.content_object

        if isinstance(obj, Customer):
            return {"type": "customer", "data": LimitedCustomerSerailizer(obj).data}
        elif isinstance(obj, Deal):
            return {"type": "deal", "data": LimitedDealSerializer(obj).data}
        elif isinstance(obj, Lead):
            return {"type": "lead", "data": LimitedLeadSerializer(obj).data}

        return None
