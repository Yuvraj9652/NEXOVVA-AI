from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.notifications.serializers import NotificationSerializer
from apps.notifications.selectors import NotificationSelector
from apps.notifications.services import NotificationService
from apps.authentication.permissions import IsOrganizationMember


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        read_filter = self.request.query_params.get("read")
        read = None
        if read_filter is not None:
            read = read_filter.lower() in ["true", "1"]

        return NotificationSelector.list_notifications(
            organization=self.request.organization,
            recipient=self.request.user,
            read=read,
        )

    @action(detail=True, methods=["post"])
    def read(self, request, pk=None):
        notification = NotificationService.mark_as_read(
            organization=request.organization,
            recipient=request.user,
            notification_id=pk,
        )
        return Response(NotificationSerializer(notification).data)
