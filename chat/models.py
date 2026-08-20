from django.db import models
from user_auth.models import User

# Create your models here.

class Chat(models.Model):
    user_id = models.ForeignKey(User, related_name="chats", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


class ChatMessage(models.Model):
    class TYPE(models.TextChoices):
            AI = "Ai", "ai"
            USER = "User", "user"
    
    chat_id = models.ForeignKey(Chat, related_name="messages", on_delete=models.CASCADE)
    role = models.CharField(max_length=255, choices=TYPE.choices, default=TYPE.USER)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)