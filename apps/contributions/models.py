from django.db import models
from django.conf import settings
from decimal import Decimal


class Contribution(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_LATE = 'late'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_PAID, 'Payée'),
        (STATUS_LATE, 'En retard'),
        (STATUS_REJECTED, 'Rejetée'),
    ]

    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_BANK = 'bank_transfer'
    PAYMENT_METHOD_MOBILE = 'mobile_money'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, 'Espèces'),
        (PAYMENT_METHOD_BANK, 'Virement bancaire'),
        (PAYMENT_METHOD_MOBILE, 'Mobile Money'),
    ]

    head = models.ForeignKey(
        'members.Head',
        on_delete=models.PROTECT,
        related_name='contributions'
    )
    cycle = models.ForeignKey(
        'cycles.Cycle',
        on_delete=models.PROTECT,
        related_name='contributions'
    )
    amount_due = models.DecimalField(
        max_digits=12, decimal_places=2,
        verbose_name='Montant dû'
    )
    amount_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Montant payé'
    )
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES,
        blank=True, verbose_name='Mode de paiement'
    )
    payment_proof = models.FileField(
        upload_to='payment_proofs/',
        blank=True, null=True,
        verbose_name='Preuve de paiement'
    )
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Référence de paiement')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='Date de soumission')
    validated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='contributions_validated'
    )
    validated_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, verbose_name='Notes admin')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contribution'
        verbose_name_plural = 'Contributions'
        unique_together = ['head', 'cycle']
        ordering = ['-created_at']

    @property
    def is_paid(self):
        return self.status == self.STATUS_PAID

    @property
    def remaining_amount(self):
        return self.amount_due - self.amount_paid

    def __str__(self):
        return f"{self.head} - {self.cycle.name} ({self.get_status_display()})"
