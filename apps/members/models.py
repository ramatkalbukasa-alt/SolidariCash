from django.db import models
from django.conf import settings


class Member(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_SUSPENDED = 'suspended'
    STATUS_BLOCKED = 'blocked'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Actif'),
        (STATUS_SUSPENDED, 'Suspendu'),
        (STATUS_BLOCKED, 'Bloqué'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    national_id = models.CharField(max_length=50, blank=True, verbose_name='Numéro national')
    emergency_contact = models.CharField(max_length=100, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspension_reason = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
        ordering = ['user__first_name', 'user__last_name']

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def head_count(self):
        return self.heads.filter(is_active=True).count()

    @property
    def is_active(self):
        return self.status == self.STATUS_ACTIVE

    def __str__(self):
        return f"{self.full_name} ({self.get_status_display()})"


class Head(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_SERVED = 'served'
    STATUS_SUSPENDED = 'suspended'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Active'),
        (STATUS_SERVED, 'Servie'),
        (STATUS_SUSPENDED, 'Suspendue'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='heads'
    )
    head_number = models.PositiveIntegerField(verbose_name='Numéro de tête')
    label = models.CharField(max_length=50, blank=True, verbose_name='Libellé')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Tête'
        verbose_name_plural = 'Têtes'
        unique_together = ['member', 'head_number']
        ordering = ['member', 'head_number']

    @property
    def display_name(self):
        return self.label or f"{self.member.full_name} - Tête #{self.head_number}"

    def __str__(self):
        return self.display_name
