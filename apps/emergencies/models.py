from django.db import models
from django.conf import settings


class Emergency(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REFUSED = 'refused'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_APPROVED, 'Approuvée'),
        (STATUS_REFUSED, 'Refusée'),
    ]

    member = models.ForeignKey(
        'members.Member',
        on_delete=models.CASCADE,
        related_name='emergencies'
    )
    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.CASCADE,
        related_name='emergencies'
    )
    head = models.ForeignKey(
        'members.Head',
        on_delete=models.CASCADE,
        related_name='emergencies',
        null=True, blank=True
    )
    reason = models.TextField(verbose_name='Motif de l\'urgence')
    justification_document = models.FileField(
        upload_to='emergency_docs/',
        blank=True, null=True,
        verbose_name='Document justificatif'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    decided_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='emergencies_decided'
    )
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_notes = models.TextField(blank=True, verbose_name='Notes de décision')
    new_position = models.PositiveIntegerField(null=True, blank=True, verbose_name='Nouvelle position assignée')

    class Meta:
        verbose_name = 'Urgence'
        verbose_name_plural = 'Urgences'
        ordering = ['-requested_at']
        constraints = [
            models.UniqueConstraint(
                fields=['member', 'cycle'],
                condition=models.Q(status__in=['pending', 'approved']),
                name='unique_active_emergency_per_cycle'
            )
        ]

    def __str__(self):
        return f"Urgence {self.member} - {self.cycle.name} ({self.get_status_display()})"
