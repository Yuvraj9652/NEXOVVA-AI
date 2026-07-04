from django.db import transaction
from apps.notifications.models import Notification


class NotificationService:
    @staticmethod
    @transaction.atomic
    def create_notification(organization, recipient, title, message, notification_type=Notification.Types.SYSTEM):
        return Notification.objects.create(
            organization=organization,
            recipient=recipient,
            title=title,
            message=message,
            notification_type=notification_type,
        )

    @staticmethod
    @transaction.atomic
    def mark_as_read(organization, recipient, notification_id):
        notification = Notification.objects.get(
            organization=organization, recipient=recipient, id=notification_id
        )
        notification.read = True
        notification.save()
        return notification
