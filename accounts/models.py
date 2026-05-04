from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    REQUESTER = 'requester', 'Requester (Club Leader / Coach)'
    APPROVER = 'approver',  'Approver (Sports Director)'
    ADMIN = 'admin',     'Administrator'


class CustomUser(AbstractUser):
    """
    CampusGrid user model.
    Institutional ID is the Student ID or Staff ID e.g. SGATWI2311.
    Admin creates accounts and sets temporary passwords.
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.REQUESTER
    )
    phone = models.CharField(
        max_length=20,
        blank=True
    )
    institutional_id = models.CharField(
        max_length=50,
        unique=True,
        default='TEMP000',
        help_text="Student ID or Staff ID e.g. SGATWI2311"
    )
    must_change_password = models.BooleanField(
        default=True,
        help_text="Forces user to change password on first login"
    )

    REQUIRED_FIELDS = ['email', 'institutional_id']

    def __str__(self):
        return f"{self.institutional_id} — {self.get_full_name() or self.username} ({self.role})"