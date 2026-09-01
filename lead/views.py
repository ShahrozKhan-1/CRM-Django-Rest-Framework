from rest_framework.response import Response
from user_auth.permissions import HasPermissions
from rest_framework.views import APIView
from .models import Lead, LeadAttachments
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from customer.models import Customer
from deal.models import Deal
from rest_framework import status
from django.db.models import Q
from utils import CloudinaryUploader




class LeadView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "lead"


    def get_queryset(self):
        user = self.request.user
        queryset = Lead.objects.filter(is_deleted=False)
        if user.is_superuser:
            return queryset
        role_name = user.roles.name.lower() if user.roles else None
        if role_name == "admin":
            return queryset
        if role_name == "manager":
            return queryset.filter(created_by=user)
        if role_name == "sale":
            return queryset.filter(Q(assigned_to=user) | Q(created_by=user)).distinct()
        return queryset.none()

    def get(self, request, lead_id=None):
        queryset = self.get_queryset()
        if lead_id:
            lead = queryset.filter(id=lead_id).first()
            serializer = LeadSerializer(lead)
            return Response({"data":serializer.data})
        leads = queryset
        serializer = LeadSerializer(leads, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = LeadSerializer(data=request.data)
        if serializer.is_valid():
            lead = serializer.save(created_by=request.user)
            
            files = request.FILES.getlist('attachments')
            if not files:
                return Response({"error": "No file provided"}, status=400)
            attachments = []
            for f in files:
                upload_data = CloudinaryUploader.upload_attachment(f)
                if upload_data.get('success'):
                    attachment = LeadAttachments.objects.create(
                        leads=lead,
                        attachment=upload_data['url'],
                        name=f.name,
                        public_id=upload_data['public_id']
                    )
                    attachments.append(attachment)
            return Response({"data":serializer.data, "message":"Lead Created Successfully"})
        
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, lead_id):
        queryset = self.get_queryset()
        if "status" in request.data:
            return Response({"Message":"Status can not be change"}, status=status.HTTP_400_BAD_REQUEST)
        lead = queryset.filter(id=lead_id).first()
        if lead.assigned_to != request.user:
            return Response({"message":"You are not allowed to update the Lead"}, status=status.HTTP_403_FORBIDDEN)

        files = request.FILES.getlist('attachments')
        if files:
            attachments = []
            for f in files:
                upload_data = CloudinaryUploader.upload_attachment(f)
                if upload_data.get('success'):
                    attachment = LeadAttachments.objects.create(
                        leads=lead,
                        attachment=upload_data['url'],
                        name=f.name,
                        public_id=upload_data['public_id']
                    )
                    attachments.append(attachment)

        serializer = LeadSerializer(lead, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(updated_by=request.user)
            return Response({"data":serializer.data, "message":"Lead Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, lead_id):
        queryset = self.get_queryset()
        lead = queryset.filter(id=lead_id).first()
        lead.is_deleted = True
        LeadAttachments.objects.filter(leads=lead).update(is_deleted=True)
        lead.save()
        return Response({"message":"Lead deleted successfully"})


class LeadStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "lead"

    def put(self, request, lead_id):
        lead = Lead.objects.get(id=lead_id, is_deleted=False)
        serializer = LeadStatusSerializer(lead, data=request.data)
        if serializer.is_valid():
            lead = serializer.save(updated_by=request.user)

            if lead.status == Lead.STATUS.QUALIFIED and not Customer.objects.filter(lead=lead).exists():
                customer = Customer.objects.create(
                    name = lead.name,
                    email = lead.email,
                    phone = lead.phone,
                    company = lead.company,
                    assigned_to = lead.assigned_to,
                    lead = lead
                )
                Deal.objects.create(
                    title = lead.name,
                    assigned_to = lead.assigned_to,
                    customer = customer,
                    lead = lead
                )

            return Response({"data":serializer.data, "message":f"Lead Status Updated"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
