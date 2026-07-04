from rest_framework import viewsets, permissions
from apps.automation.models import AutomationRule
from apps.automation.serializers import AutomationRuleSerializer
from apps.authentication.permissions import IsOrganizationMember, IsAdminUserRole


class AutomationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAdminUserRole]

    def get_queryset(self):
        return AutomationRule.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)
