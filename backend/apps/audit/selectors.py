from apps.audit.models import ActivityLog


class AuditSelector:
    @staticmethod
    def list_activities(organization, target_type=None, target_id=None):
        queryset = ActivityLog.objects.filter(organization=organization).select_related("user")
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        if target_id:
            queryset = queryset.filter(target_id=target_id)
        return queryset
