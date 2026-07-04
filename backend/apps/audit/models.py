from django.db import models
from django.conf import settings
from apps.common.models import TenantModel


class ActivityLog(TenantModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activities",
    )
    action = models.CharField(max_length=100)  # e.g., "lead_created", "deal_stage_updated"
    target_type = models.CharField(max_length=100)  # e.g., "lead", "contact", "deal"
    target_id = models.IntegerField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username if self.user else 'System'} - {self.action} - {self.created_at}"
