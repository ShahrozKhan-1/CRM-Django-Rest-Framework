from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class ROLES_CHOICES(models.TextChoices):
        ADMIN = 'Admin', 'admin'
        MANAGER = 'Manager', 'manager'
        SALES = 'Sales', 'sales'
        SUPPORT = 'Support', 'support'

    email = models.EmailField(unique=True)
    roles = models.CharField(max_length=255, choices=ROLES_CHOICES.choices, default=ROLES_CHOICES.SALES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']