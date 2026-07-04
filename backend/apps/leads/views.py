from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from apps.leads.serializers import LeadSerializer
from apps.leads.selectors import LeadSelector
from apps.leads.services import LeadService
from apps.authentication.permissions import IsOrganizationMember


class LeadViewSet(viewsets.ModelViewSet):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        status_filter = self.request.query_params.get("status")
        return LeadSelector.list_leads(
            organization=self.request.organization,
            search_query=search_query,
            status=status_filter,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        contact = validated_data.pop("contact", None)
        company = validated_data.pop("company", None)

        lead = LeadService.create_lead(
            organization=self.request.organization,
            user=self.request.user,
            contact_id=contact.id if contact else None,
            company_id=company.id if company else None,
            **validated_data,
        )
        serializer.instance = lead

    def perform_update(self, serializer):
        validated_data = serializer.validated_data

        contact_id = None
        if "contact" in validated_data:
            contact = validated_data.pop("contact")
            contact_id = contact.id if contact else None
        elif self.get_object().contact:
            contact_id = self.get_object().contact.id

        company_id = None
        if "company" in validated_data:
            company = validated_data.pop("company")
            company_id = company.id if company else None
        elif self.get_object().company:
            company_id = self.get_object().company.id

        lead = LeadService.update_lead(
            organization=self.request.organization,
            user=self.request.user,
            lead_id=self.get_object().id,
            contact_id=contact_id,
            company_id=company_id,
            **validated_data,
        )
        serializer.instance = lead

    def perform_destroy(self, instance):
        LeadService.delete_lead(
            organization=self.request.organization,
            user=self.request.user,
            lead_id=instance.id,
        )

    @action(detail=True, methods=["get"])
    def matches(self, request, pk=None):
        from apps.ai.services import PropertyMatchmakerService
        from rest_framework.response import Response

        lead = self.get_object()
        recommendation = PropertyMatchmakerService.match_properties_for_lead(
            organization=request.organization,
            user=request.user,
            lead_id=lead.id
        )
        return Response({"recommendation": recommendation})
