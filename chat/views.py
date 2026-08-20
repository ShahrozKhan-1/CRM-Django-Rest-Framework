from rest_framework.response import Response
from user_auth.permissions import HasPermissions
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import *
from chat.models import *
from rest_framework import status
from .serializers import *



class ChatView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "chat"


    def get(self, request):
        chat = Chat.objects.filter(is_deleted=False).order_by("-created_at")
        serializer = ChatSerializer(chat, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request):
        instance = request.data
        serializer = ChatSerializer(data=instance)
        if serializer.is_valid():
            serializer.save(user_id=request.user)
            return Response({"data":serializer.data, "message":"Chat Created Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Creating Chat"})
    
    def delete(self, request, chat_id):
        chat = Chat.objects.get(id=chat_id, is_deleted=False)
        chat.is_deleted = True
        chat.save()
        return Response({"message":"Chat deleted successfully"})



class ChatMessageView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [HasPermissions]
    permission_name = "chat"


    def get(self, request, chat_id):
        chatmessage = ChatMessage.objects.filter(is_deleted=False, chat_id=chat_id).order_by("-created_at")
        serializer = ChatMessageSerializer(chatmessage, many=True)
        return Response({"data":serializer.data})
    
    def post(self, request, chat_id):
        chat = Chat.objects.get(id=chat_id, is_deleted=False, user_id=request.user)
        instance = request.data
        serializer = ChatMessageSerializer(data=instance)
        if serializer.is_valid():
            serializer.save(chat_id=chat)
            return Response({"data":serializer.data, "message":"Message Send Successffully"})
        return Response({"data":serializer.errors, "message":"Error While Sending Message"})
