import logging
from apps.automation.models import AutomationRule
from apps.notifications.services import NotificationService
from apps.tasks.services import TasksService

logger = logging.getLogger(__name__)


class EventBus:
    @staticmethod
    def dispatch_event(organization, user, event_name, target_id, context=None):
        """Dispatches triggers to resolve active automation rules for this organization."""
        rules = AutomationRule.objects.filter(
            organization=organization, trigger_event=event_name, active=True
        )

        for rule in rules:
            try:
                if rule.action_type == AutomationRule.ActionTypes.SEND_NOTIFICATION:
                    recipient_id = rule.action_params.get("recipient_id") or user.id
                    from django.contrib.auth import get_user_model

                    User = get_user_model()
                    recipient = User.objects.get(id=recipient_id)

                    NotificationService.create_notification(
                        organization=organization,
                        recipient=recipient,
                        title=rule.action_params.get("title", "Automated Action Triggered"),
                        message=rule.action_params.get("message", "Rule triggered."),
                        notification_type="SYSTEM",
                    )
                elif rule.action_type == AutomationRule.ActionTypes.CREATE_TASK:
                    TasksService.create_task(
                        organization=organization,
                        user=user,
                        title=rule.action_params.get("title", "Follow-up required"),
                        description=rule.action_params.get("description", "Automated follow-up task."),
                        assigned_to_id=rule.action_params.get("assigned_to_id") or user.id,
                        lead_id=target_id if event_name == "lead_created" else None,
                    )
                elif rule.action_type == AutomationRule.ActionTypes.ENRICH_LEAD:
                    if event_name == "lead_created":
                        from apps.crm.tasks import enrich_lead_via_ai
                        enrich_lead_via_ai.delay(target_id)
                logger.info(f"Fired automation rule: {rule.name} for event {event_name}")
            except Exception as e:
                logger.error(f"Failed to execute automation rule {rule.id}: {str(e)}")
