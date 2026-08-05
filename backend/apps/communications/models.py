from django.db import models
from apps.common.models import TenantModel


class BroadcastCampaign(TenantModel):
    class Statuses(models.TextChoices):
        ACTIVE = "Active", "Active"
        SCHEDULED = "Scheduled", "Scheduled"
        COMPLETED = "Completed", "Completed"
        DRAFT = "Draft", "Draft"

    class TargetTypes(models.TextChoices):
        AI_MATCHED = "AI_MATCHED", "AI Customer Matched"
        SELECTED_CUSTOMERS = "SELECTED_CUSTOMERS", "Selected Existing Customers"
        CSV_UPLOAD = "CSV_UPLOAD", "CSV Customer Upload"
        ALL_CUSTOMERS = "ALL_CUSTOMERS", "All System Customers"

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=Statuses.choices, default=Statuses.DRAFT
    )
    target_type = models.CharField(
        max_length=30, choices=TargetTypes.choices, default=TargetTypes.AI_MATCHED
    )
    project = models.ForeignKey(
        "properties.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comm_broadcast_campaigns",
    )
    selected_customer_ids = models.JSONField(default=list, blank=True)
    reach = models.CharField(max_length=50, blank=True, default="0")
    total_sent = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    image_url = models.URLField(max_length=500, blank=True, default="")
    content = models.TextField(blank=True, default="")
    date = models.DateField(null=True, blank=True)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"
