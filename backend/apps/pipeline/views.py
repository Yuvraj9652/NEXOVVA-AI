from rest_framework import viewsets, permissions
from apps.pipeline.serializers import PipelineStageSerializer, DealSerializer
from apps.pipeline.selectors import PipelineSelector
from apps.pipeline.services import PipelineService
from apps.authentication.permissions import IsOrganizationMember


class PipelineStageViewSet(viewsets.ModelViewSet):
    serializer_class = PipelineStageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return PipelineSelector.list_stages(organization=self.request.organization)

    def perform_create(self, serializer):
        stage = PipelineService.create_stage(
            organization=self.request.organization,
            user=self.request.user,
            **serializer.validated_data,
        )
        serializer.instance = stage


class DealViewSet(viewsets.ModelViewSet):
    serializer_class = DealSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        stage_id = self.request.query_params.get("stage")
        return PipelineSelector.list_deals(
            organization=self.request.organization,
            search_query=search_query,
            stage_id=stage_id,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        stage = validated_data.pop("stage")
        assigned_to = validated_data.pop("assigned_to", None)
        contact = validated_data.pop("contact", None)
        company = validated_data.pop("company", None)

        deal = PipelineService.create_deal(
            organization=self.request.organization,
            user=self.request.user,
            stage_id=stage.id,
            assigned_to_id=assigned_to.id if assigned_to else None,
            contact_id=contact.id if contact else None,
            company_id=company.id if company else None,
            **validated_data,
        )
        serializer.instance = deal

    def perform_update(self, serializer):
        validated_data = serializer.validated_data

        stage_id = None
        if "stage" in validated_data:
            stage_id = validated_data.pop("stage").id
        elif self.get_object().stage:
            stage_id = self.get_object().stage.id

        assigned_to_id = None
        if "assigned_to" in validated_data:
            assigned_to = validated_data.pop("assigned_to")
            assigned_to_id = assigned_to.id if assigned_to else None
        elif self.get_object().assigned_to:
            assigned_to_id = self.get_object().assigned_to.id

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

        deal = PipelineService.update_deal(
            organization=self.request.organization,
            user=self.request.user,
            deal_id=self.get_object().id,
            stage_id=stage_id,
            assigned_to_id=assigned_to_id,
            contact_id=contact_id,
            company_id=company_id,
            **validated_data,
        )
        serializer.instance = deal

    def perform_destroy(self, instance):
        PipelineService.delete_deal(
            organization=self.request.organization,
            user=self.request.user,
            deal_id=instance.id,
        )
