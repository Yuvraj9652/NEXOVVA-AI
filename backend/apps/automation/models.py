from django.db import models
from apps.common.models import TenantModel


class AutomationRule(TenantModel):
    class TriggerEvents(models.TextChoices):
        LEAD_CREATED = "lead_created", "Lead Created"
        DEAL_STAGE_CHANGED = "deal_stage_changed", "Deal Stage Changed"
        TASK_COMPLETED = "task_completed", "Task Completed"

    class ActionTypes(models.TextChoices):
        SEND_NOTIFICATION = "send_notification", "Send Notification"
        CREATE_TASK = "create_task", "Create Task"
        ENRICH_LEAD = "enrich_lead", "Enrich Lead via AI"

    name = models.CharField(max_length=255)
    trigger_event = models.CharField(
        max_length=50, choices=TriggerEvents.choices, default=TriggerEvents.LEAD_CREATED
    )
    action_type = models.CharField(
        max_length=50, choices=ActionTypes.choices, default=ActionTypes.SEND_NOTIFICATION
    )
    action_params = models.JSONField(default=dict, blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.trigger_event} -> {self.action_type})"
