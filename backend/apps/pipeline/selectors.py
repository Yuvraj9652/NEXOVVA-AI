from apps.pipeline.models import PipelineStage, Deal


class PipelineSelector:
    @staticmethod
    def list_stages(organization):
        return PipelineStage.objects.filter(organization=organization).order_by("order", "created_at")

    @staticmethod
    def list_deals(organization, search_query=None, stage_id=None):
        queryset = Deal.objects.filter(organization=organization).select_related(
            "stage", "assigned_to", "contact", "company"
        )
        if stage_id:
            queryset = queryset.filter(stage_id=stage_id)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
        return queryset

    @staticmethod
    def get_deal_by_id(organization, deal_id):
        return Deal.objects.select_related("stage", "assigned_to", "contact", "company").get(
            organization=organization, id=deal_id
        )
