from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class Attachment(models.Model):
    file = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    public_id = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    is_deleted = models.BooleanField(default=False)