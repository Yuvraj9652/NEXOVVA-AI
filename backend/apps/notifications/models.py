from django.db import models
from django.conf import settings
from apps.common.models import TenantModel


class Notification(TenantModel):
    class Types(models.TextChoices):
        TASK_REMINDER = "TASK_REMINDER", "Task Reminder"
        LEAD_ASSIGNED = "LEAD_ASSIGNED", "Lead Assigned"
        DEAL_WON = "DEAL_WON", "Deal Won"
        SYSTEM = "SYSTEM", "System Alert"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    read = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=30, choices=Types.choices, default=Types.SYSTEM
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.recipient.username} - {self.title} ({'Read' if self.read else 'Unread'})"
