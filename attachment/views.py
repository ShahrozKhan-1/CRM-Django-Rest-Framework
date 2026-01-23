from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.authentication import JWTAuthentication
from user_auth.permissions import *
from customer.models import Customer
from lead.models import Lead
from deal.models import Deal
from .models import Attachment
from rest_framework.views import APIView
from django.contrib.contenttypes.models import ContentType
from .serializers import *
from rest_framework.response import Response
from utils import CloudinaryUploader




class CustomerAttachment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AttachmentObjectPermission]

    def get(self, request, customer_id=None):
        content_type = ContentType.objects.get_for_model(Customer)
        qs = Attachment.objects.filter(content_type=content_type)
        if customer_id:
            customer = get_object_or_404(Customer, id=customer_id)
            qs = qs.filter(object_id=customer.id)

        user = request.user
        if user.roles == 'Sales':
            qs = qs.filter(
                object_id__in=Customer.objects.filter(
                    assigned_to=user
                ).values_list('id', flat=True)
            )
        elif user.roles == 'Manager':
            qs = qs.filter(
                object_id__in=Customer.objects.filter(
                    assigned_to__manager=user
                ).values_list('id', flat=True)
            )
        serializer = AttachmentSerializer(qs, many=True)
        return Response({"data": serializer.data})

    
    
    def post(self, request, customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        self.check_object_permissions(request, Attachment(content_object=customer))
        files = request.FILES.getlist('file')
        if not files:
            return Response({"error": "No file provided"}, status=400)
        attachments = []
        for f in files:
            upload_data = CloudinaryUploader.upload_attachment(f)

            if upload_data.get('success'):
                attachment = Attachment.objects.create(
                    content_object=customer,
                    file=upload_data['url'],
                    name=f.name,
                    public_id=upload_data['public_id']
                )
                attachments.append(attachment)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=201)



class DealAttachment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AttachmentObjectPermission]

    def get(self, request, deal_id):
        content_type = ContentType.objects.get_for_model(Deal)
        if deal_id:
            self.check_object_permissions(request, deal)
            deal = get_object_or_404(Deal, id=deal_id)
            attachments = Attachment.objects.filter(content_type=content_type, object_id=deal.id)
        else:
            attachments = Attachment.objects.filter(content_type=content_type)
        
        serializer = AttachmentSerializer(attachments, many=True)
        return Response({"data":serializer.data})
    

    def post(self, request, deal_id):
        deal = get_object_or_404(Deal, id=deal_id)
        self.check_object_permissions(request, Attachment(content_object=deal))
        files = request.FILES.getlist('file')
        if not files:
            return Response({"error": "No file provided"}, status=400)
        attachments = []
        for f in files:
            upload_data = CloudinaryUploader.upload_attachment(f)

            if upload_data.get('success'):
                attachment = Attachment.objects.create(
                    content_object=deal,
                    file=upload_data['url'],
                    name=f.name,
                    public_id=upload_data['public_id']
                )
                attachments.append(attachment)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=201)


class LeadAttachment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AttachmentObjectPermission]

    def get(self, request, lead_id):
        content_type = ContentType.objects.get_for_model(Lead)
        if lead_id:
            self.check_object_permissions(request, lead)
            lead = get_object_or_404(Lead, id=lead_id)
            attachments = Attachment.objects.filter(content_type=content_type, object_id=lead.id)
        else:
            attachments = Attachment.objects.filter(content_type=content_type)
        
        serializer = AttachmentSerializer(attachments, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request, lead_id):
        lead = get_object_or_404(Lead, id=lead_id)
        self.check_object_permissions(request, Attachment(content_object=lead))
        files = request.FILES.getlist('file')
        if not files:
            return Response({"error": "No file provided"}, status=400)
        attachments = []
        for f in files:
            upload_data = CloudinaryUploader.upload_attachment(f)

            if upload_data.get('success'):
                attachment = Attachment.objects.create(
                    content_object=lead,
                    file=upload_data['url'],
                    name=f.name,
                    public_id=upload_data['public_id']
                )
                attachments.append(attachment)
        serializer = AttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=201)