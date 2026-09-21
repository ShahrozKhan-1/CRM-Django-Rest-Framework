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



class AgentActionLog(models.Model):
    class Status(models.TextChoices):
        SUCCESS = "success", "Success"
        ERROR = "error", "Error"

    user = models.ForeignKey(User, related_name="agent_logs", on_delete=models.CASCADE)
    session_id = models.CharField(max_length=128, blank=True)

    user_query = models.CharField(blank=True)
    tool_name = models.CharField(max_length=128)
    operation = models.CharField(max_length=32, blank=True)

    input_data = models.JSONField(default=dict, blank=True)
    output_data = models.JSONField(default=dict, blank=True)
    entity_type = models.CharField(max_length=32, blank=True)
    entity_id = models.IntegerField(null=True, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUCCESS)
    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
