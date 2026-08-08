from apps.broadcast.models import Campaign, CampaignMessage, CampaignLog, AudienceSegment, ContactList, BroadcastTemplate


class BroadcastRepository:
    """Repository layer for Broadcast app."""

    @staticmethod
    def get_campaigns(organization, filters=None):
        queryset = Campaign.objects.filter(organization=organization)
        if filters:
            status = filters.get("status")
            campaign_type = filters.get("campaign_type")
            if status:
                queryset = queryset.filter(status=status)
            if campaign_type:
                queryset = queryset.filter(campaign_type=campaign_type)
        return queryset.order_by("-created_at")

    @staticmethod
    def get_campaign_by_id(organization, campaign_id):
        return Campaign.objects.filter(organization=organization, id=campaign_id).first()

    @staticmethod
    def get_messages(campaign_id=None, organization=None):
        queryset = CampaignMessage.objects.filter(organization=organization)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset.order_by("-created_at")

    @staticmethod
    def get_audience_segments(organization):
        return AudienceSegment.objects.filter(organization=organization).order_by("-created_at")

    @staticmethod
    def get_contact_lists(organization):
        return ContactList.objects.filter(organization=organization).order_by("-created_at")

    @staticmethod
    def get_templates(organization):
        return BroadcastTemplate.objects.filter(organization=organization).order_by("-created_at")

    @staticmethod
    def get_logs(campaign_id=None, organization=None):
        queryset = CampaignLog.objects.filter(organization=organization)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset.order_by("-created_at")

    @staticmethod
    def get_analytics(campaign_id=None, organization=None):
        if campaign_id:
            return CampaignAnalytics.objects.filter(organization=organization, campaign_id=campaign_id).first()
        return CampaignAnalytics.objects.filter(organization=organization)

    @staticmethod
    def check_duplicate_contact(organization, campaign_id, customer_phone, customer_email=""):
        existing = CampaignMessage.objects.filter(
            organization=organization,
            campaign_id=campaign_id,
        )
        if customer_phone:
            existing = existing.filter(customer_phone=customer_phone)
        if customer_email:
            existing = existing.filter(customer_email=customer_email)
        return existing.exists()