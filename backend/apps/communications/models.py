from django.db import models
from apps.common.models import TenantModel


class BroadcastCampaign(TenantModel):
    class Statuses(models.TextChoices):
        ACTIVE = "Active", "Active"
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        DRAFT = "Draft", "Draft"

    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=Statuses.choices, default=Statuses.DRAFT
    )
    reach = models.CharField(max_length=50, blank=True, default="-")
    date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"
