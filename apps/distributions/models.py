from django.db import models
from django.conf import settings
from decimal import Decimal


class Distribution(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_COMPLETED, 'Effectuée'),
        (STATUS_FAILED, 'Échouée'),
        (STATUS_CANCELLED, 'Annulée'),
    ]

    rotation_order = models.OneToOneField(
        'rotation.RotationOrder',
        on_delete=models.PROTECT,
        related_name='distribution'
    )
    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.PROTECT,
        related_name='distributions'
    )
    head = models.ForeignKey(
        'members.Head',
        on_delete=models.PROTECT,
        related_name='distributions'
    )
    gross_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Montant brut'
    )
    commission_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Commission'
    )
    net_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Montant net distribué'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='distributions_processed'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    failure_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Distribution'
        verbose_name_plural = 'Distributions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Distribution {self.head} - {self.cycle.name} ({self.get_status_display()})"
