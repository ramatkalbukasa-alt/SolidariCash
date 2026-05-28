from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    ACTION_CREATE = 'CREATE'
    ACTION_UPDATE = 'UPDATE'
    ACTION_DELETE = 'DELETE'
    ACTION_LOGIN = 'LOGIN'
    ACTION_LOGOUT = 'LOGOUT'
    ACTION_VALIDATE = 'VALIDATE'
    ACTION_DISTRIBUTE = 'DISTRIBUTE'
    ACTION_SUSPEND = 'SUSPEND'
    ACTION_APPROVE = 'APPROVE'
    ACTION_REFUSE = 'REFUSE'
    ACTION_CHOICES = [
        (ACTION_CREATE, 'Création'),
        (ACTION_UPDATE, 'Modification'),
        (ACTION_DELETE, 'Suppression'),
        (ACTION_LOGIN, 'Connexion'),
        (ACTION_LOGOUT, 'Déconnexion'),
        (ACTION_VALIDATE, 'Validation'),
        (ACTION_DISTRIBUTE, 'Distribution'),
        (ACTION_SUSPEND, 'Suspension'),
        (ACTION_APPROVE, 'Approbation'),
        (ACTION_REFUSE, 'Refus'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=50, blank=True)
    object_repr = models.CharField(max_length=200, blank=True)
    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Journal d\'audit'
        verbose_name_plural = 'Journaux d\'audit'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} - {self.model_name} #{self.object_id} par {self.user} @ {self.timestamp}"
