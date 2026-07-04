from apps.audit.models import ActivityLog


class ActivityLogService:
    @staticmethod
    def log_activity(organization, user, action, target_type, target_id, description):
        return ActivityLog.objects.create(
            organization=organization,
            user=user,
            action=action,
            target_type=target_type,
            target_id=target_id,
            description=description,
        )
