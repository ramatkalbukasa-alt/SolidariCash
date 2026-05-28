from django.db import models
from django.conf import settings
from decimal import Decimal


class Cycle(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_OPEN = 'open'
    STATUS_DISTRIBUTION = 'distribution'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_OPEN, 'Ouvert - Contributions'),
        (STATUS_DISTRIBUTION, 'Distribution en cours'),
        (STATUS_CLOSED, 'Clôturé'),
    ]

    name = models.CharField(max_length=100, verbose_name='Nom du cycle')
    description = models.TextField(blank=True)
    start_date = models.DateField(verbose_name='Date de début')
    end_date = models.DateField(verbose_name='Date de fin')
    contribution_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Montant par tête'
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=4,
        default=Decimal('0.0200'),
        verbose_name='Taux de commission (%)'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='cycles_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Cycle'
        verbose_name_plural = 'Cycles'
        ordering = ['-start_date']

    @property
    def total_collected(self):
        from apps.contributions.models import Contribution
        total = self.contributions.filter(
            status=Contribution.STATUS_PAID
        ).aggregate(
            total=models.Sum('amount_paid')
        )['total'] or Decimal('0.00')
        return total

    @property
    def commission_amount(self):
        return self.total_collected * self.commission_rate

    @property
    def distributable_amount(self):
        return self.total_collected - self.commission_amount

    @property
    def total_heads(self):
        from apps.rotation.models import RotationOrder
        return self.rotation_orders.count()

    @property
    def is_open(self):
        return self.status == self.STATUS_OPEN

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
