from django.contrib.auth.models import AbstractUser
from django.db import models



class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)


class User(AbstractUser):

    email = models.EmailField(unique=True)
    roles = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True, related_name="users")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} - {self.roles.name}"


class Permission(models.Model):
    role = models.ForeignKey(Role, related_name="permission", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    actions = models.JSONField(default=list)

    def __str__(self):
        return f"{self.role.name} - {self.name}"