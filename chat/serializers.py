from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from .models import Chat, ChatMessage



class ChatSerializer(ModelSerializer):
    user_id = PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Chat
        exclude = ['is_deleted']


class ChatMessageSerializer(ModelSerializer):
    chat_id = PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = ChatMessage
        exclude = ['is_deleted']