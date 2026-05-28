from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_INFO = 'info'
    TYPE_SUCCESS = 'success'
    TYPE_WARNING = 'warning'
    TYPE_ERROR = 'error'
    TYPE_CHOICES = [
        (TYPE_INFO, 'Information'),
        (TYPE_SUCCESS, 'Succès'),
        (TYPE_WARNING, 'Avertissement'),
        (TYPE_ERROR, 'Erreur'),
    ]

    CATEGORY_CYCLE = 'cycle'
    CATEGORY_CONTRIBUTION = 'contribution'
    CATEGORY_DISTRIBUTION = 'distribution'
    CATEGORY_EMERGENCY = 'emergency'
    CATEGORY_SYSTEM = 'system'
    CATEGORY_CHOICES = [
        (CATEGORY_CYCLE, 'Cycle'),
        (CATEGORY_CONTRIBUTION, 'Contribution'),
        (CATEGORY_DISTRIBUTION, 'Distribution'),
        (CATEGORY_EMERGENCY, 'Urgence'),
        (CATEGORY_SYSTEM, 'Système'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200, verbose_name='Titre')
    message = models.TextField(verbose_name='Message')
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_INFO)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_SYSTEM)
    is_read = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient.username}"
