from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(unique=True)
    roles = models.CharField(max_length=255)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)



class Permission(models.Model):
    role = models.ForeignKey(Role, related_name="permission", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    actions = models.JSONField(default=list)