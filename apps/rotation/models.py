from django.db import models
from django.conf import settings


class RotationOrder(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_SERVED = 'served'
    STATUS_SKIPPED = 'skipped'
    STATUS_POSTPONED = 'postponed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_SERVED, 'Servi'),
        (STATUS_SKIPPED, 'Ignoré'),
        (STATUS_POSTPONED, 'Reporté'),
    ]

    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.CASCADE,
        related_name='rotation_orders'
    )
    head = models.ForeignKey(
        'members.Head',
        on_delete=models.CASCADE,
        related_name='rotation_orders'
    )
    position = models.PositiveIntegerField(verbose_name='Position dans la rotation')
    original_position = models.PositiveIntegerField(verbose_name='Position originale')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_emergency = models.BooleanField(default=False)
    scheduled_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ordre de rotation'
        verbose_name_plural = 'Ordres de rotation'
        unique_together = ['cycle', 'head']
        ordering = ['cycle', 'position']

    def __str__(self):
        return f"Position {self.position}: {self.head} - Cycle {self.cycle.name}"


class RotationHistory(models.Model):
    ACTION_CREATED = 'created'
    ACTION_MODIFIED = 'modified'
    ACTION_EMERGENCY = 'emergency'
    ACTION_POSTPONED = 'postponed'
    ACTION_RESTORED = 'restored'
    ACTION_CHOICES = [
        (ACTION_CREATED, 'Création'),
        (ACTION_MODIFIED, 'Modification'),
        (ACTION_EMERGENCY, 'Urgence'),
        (ACTION_POSTPONED, 'Report'),
        (ACTION_RESTORED, 'Restauration'),
    ]

    rotation_order = models.ForeignKey(
        RotationOrder,
        on_delete=models.CASCADE,
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_position = models.PositiveIntegerField(null=True, blank=True)
    new_position = models.PositiveIntegerField(null=True, blank=True)
    reason = models.TextField(blank=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Historique de rotation'
        verbose_name_plural = 'Historiques de rotation'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.get_action_display()} - {self.rotation_order} - {self.changed_at}"
