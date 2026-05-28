from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender='contributions.Contribution')
def contribution_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status == 'late':
        from .utils import send_notification
        send_notification(
            instance.head.member.user,
            'Contribution en retard',
            f"Votre contribution pour le cycle {instance.cycle.name} est en retard. Régularisez au plus vite.",
            notification_type='warning',
            category='contribution',
            send_email=True,
        )


@receiver(post_save, sender='cycles.Cycle')
def cycle_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status == 'open':
        from .utils import send_bulk_notification
        send_bulk_notification(
            'Cycle ouvert',
            f"Le cycle '{instance.name}' est maintenant ouvert. Les contributions sont acceptées.",
            notification_type='info',
            category='cycle',
        )
