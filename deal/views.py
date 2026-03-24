from rest_framework.response import Response
from user_auth.permissions import HasPermissions
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from deal.models import Deal, DealAttachments
from rest_framework import status
from .serializers import *
from utils import CloudinaryUploader




class DealView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "deal"


    def get(self, request):
        deal = Deal.objects.filter(is_deleted=False)
        serializer = DealSerializer(deal, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        serializer = DealSerializer(data=request.data)
        if serializer.is_valid():
            deal = serializer.save()
            
            files = request.FILES.getlist('attachments')
            if not files:
                return Response({"error": "No file provided"}, status=400)
            attachments = []
            for f in files:
                upload_data = CloudinaryUploader.upload_attachment(f)
                if upload_data.get('success'):
                    attachment = DealAttachments.objects.create(
                        deals=deal,
                        attachments=upload_data['url'],
                        name=f.name,
                        public_id=upload_data['public_id']
                    )
                    attachments.append(attachment)
            return Response({"data":serializer.data, "message":"Deal Created Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        deal.is_deleted = True
        DealAttachments.objects.filter(deals=deal).update(is_deleted=True)
        deal.save()
        return Response({"message":"Deal deleted successfully"})


class UserDealView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "deal"

    def get(self, request):
        deal = Deal.objects.filter(assigned_to=request.user)
        serializer = DealSerializer(deal, many=True)
        return Response({"data":serializer.data})
    

    def put(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        serializer = DealSerializer(deal, data=request.data, partial=True)

        files = request.FILES.getlist('attachments')
        if not files:
            return Response({"error": "No file provided"}, status=400)
        attachments = []
        for f in files:
            upload_data = CloudinaryUploader.upload_attachment(f)

            if upload_data.get('success'):
                attachment = DealAttachments.objects.create(
                    deals = deal,
                    attachments=upload_data['url'],
                    name=f.name,
                    public_id=upload_data['public_id']
                )
                attachments.append(attachment)

        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Deal Updated Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DealStatus(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "deal"

    def put(self, request, deal_id):
        deal = Deal.objects.get(id=deal_id, is_deleted=False)
        serializer = DealStageSerializer(deal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"data":serializer.data, "message":"Deal Stage changed Successfully"})
        return Response({"Message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
