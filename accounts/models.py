from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    REQUESTER = 'requester', 'Requester'
    APPROVER = 'approver',  'Approver'
    ADMIN = 'admin',     'Admin'


class CustomUser(AbstractUser):
    role = models.CharField(
        max_length=20, choices=Role.choices, default=Role.REQUESTER)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
