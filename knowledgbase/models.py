from django.db import models


class KnowledgeDocument(models.Model):
    class STATUS(models.TextChoices):
        PENDING = 'Pending', 'pending'
        COMPLETED = 'Completed', 'completed'

    title = models.CharField(max_length=255)
    file = models.CharField(max_length=255)
    public_id = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.PENDING)
    uploaded_at = models.DateTimeField(auto_now_add=True)
