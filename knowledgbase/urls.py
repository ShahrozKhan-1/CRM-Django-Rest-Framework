from django.urls import path
from .views import KnowledgeDocumentView


urlpatterns = [
    path("knowledge-documents/", KnowledgeDocumentView.as_view(), name="knowledge-documents"),
    path("knowledge-documents/<int:doc_id>/", KnowledgeDocumentView.as_view(), name="knowledge-document-delete"),
]