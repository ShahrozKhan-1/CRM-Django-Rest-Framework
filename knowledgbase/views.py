from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import KnowledgeDocumentSerializer
from .models import KnowledgeDocument
from rest_framework_simplejwt.authentication import JWTAuthentication
from user_auth.permissions import HasPermissions
from utils import CloudinaryUploader
from rest_framework import status
from .utils import create_embeddings


class KnowledgeDocumentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "knowledge-base"

    def get(self, request):
        data = KnowledgeDocument.objects.all()
        serializer = KnowledgeDocumentSerializer(data, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):            
        files = request.FILES.getlist('attachments')
        if not files:
            return Response({"error": "No file provided"}, status=400)
        attachments = []
        for f in files:
            upload_data = CloudinaryUploader.upload_attachment(f)
            if upload_data.get('success'):
                attachment = KnowledgeDocument.objects.create(

                    file=upload_data['url'],
                    title=f.name,
                    public_id=upload_data['public_id'],
                    status=KnowledgeDocument.STATUS.PENDING
                )
                attachments.append(attachment)
        create_embeddings(attachments)
        serializer = KnowledgeDocumentSerializer(attachments, many=True)
        return Response({"data":serializer.data, "message":"Document Added Successfully"})
        
    
    def delete(self, request, doc_id):
        doc = KnowledgeDocument.objects.filter(id=doc_id)
        doc.delete()
        return Response({"message":"document deleted successfully"})
