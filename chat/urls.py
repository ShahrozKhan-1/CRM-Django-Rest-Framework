from django.urls import path
from .views import *


urlpatterns = [
    path("conversation/", ChatView.as_view()),
    path("conversation/<int:chat_id>/", ChatView.as_view()),
    path("conversation/<int:chat_id>/messages/", ChatMessageView.as_view()),
]