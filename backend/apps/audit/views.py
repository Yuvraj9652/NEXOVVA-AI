from rest_framework import mixins, viewsets, permissions
from apps.audit.serializers import ActivityLogSerializer
from apps.audit.selectors import AuditSelector
from apps.authentication.permissions import IsOrganizationMember, IsManagerUserRole


class ActivityLogViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = ActivityLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsManagerUserRole]

    def get_queryset(self):
        target_type = self.request.query_params.get("target_type")
        target_id = self.request.query_params.get("target_id")
        return AuditSelector.list_activities(
            organization=self.request.organization,
            target_type=target_type,
            target_id=target_id,
        )
