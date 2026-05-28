from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_ADMIN = 'admin'
    ROLE_MEMBER = 'member'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Administrateur'),
        (ROLE_MEMBER, 'Membre'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_MEMBER)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    @property
    def is_admin(self):
        return self.role == self.ROLE_ADMIN

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"
