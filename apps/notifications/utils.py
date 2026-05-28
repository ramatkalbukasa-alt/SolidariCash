from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Notification


def send_notification(user, title, message, notification_type='info', category='system', send_email=False):
    """Créer une notification in-app et optionnellement envoyer un email."""
    notif = Notification.objects.create(
        recipient=user,
        title=title,
        message=message,
        notification_type=notification_type,
        category=category,
    )

    if send_email and user.email:
        try:
            send_mail(
                subject=f"[SolidariCash] {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
            notif.is_email_sent = True
            notif.save(update_fields=['is_email_sent'])
        except Exception:
            pass

    return notif


def send_bulk_notification(title, message, notification_type='info', category='system', send_email=False):
    """Envoyer une notification à tous les utilisateurs actifs."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    users = User.objects.filter(is_active=True)
    notifications = []
    for user in users:
        notifications.append(Notification(
            recipient=user,
            title=title,
            message=message,
            notification_type=notification_type,
            category=category,
        ))
    Notification.objects.bulk_create(notifications)

    if send_email:
        emails = [u.email for u in users if u.email]
        if emails:
            try:
                send_mail(
                    subject=f"[SolidariCash] {title}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=emails,
                    fail_silently=True,
                )
            except Exception:
                pass
