from apps.notifications.models import Notification


class NotificationSelector:
    @staticmethod
    def list_notifications(organization, recipient, read=None):
        queryset = Notification.objects.filter(organization=organization, recipient=recipient)
        if read is not None:
            queryset = queryset.filter(read=read)
        return queryset

    @staticmethod
    def get_notification(organization, recipient, notification_id):
        return Notification.objects.get(
            organization=organization, recipient=recipient, id=notification_id
        )
