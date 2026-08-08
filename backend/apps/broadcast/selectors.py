from apps.broadcast.repositories import BroadcastRepository


class BroadcastSelector:
    """Selector layer for Broadcast app."""

    @staticmethod
    def get_campaign_summary(organization):
        campaigns = BroadcastRepository.get_campaigns(organization)
        return {
            "total": campaigns.count(),
            "active": campaigns.filter(status="Active").count(),
            "running": campaigns.filter(status="Running").count(),
            "scheduled": campaigns.filter(status="Scheduled").count(),
            "completed": campaigns.filter(status="Completed").count(),
            "failed": campaigns.filter(status="Failed").count(),
            "draft": campaigns.filter(status="Draft").count(),
            "paused": campaigns.filter(status="Paused").count(),
            "cancelled": campaigns.filter(status="Cancelled").count(),
        }

    @staticmethod
    def get_audience_match_results(query, filters=None):
        from apps.customers.models import Customer
        qs = Customer.objects.filter(organization=query.organization if hasattr(query, 'organization') else None)
        if filters:
            budget = filters.get("budget")
            city = filters.get("city")
            builder = filters.get("builder")
            configuration = filters.get("configuration")
            occupation = filters.get("occupation")
            lead_score = filters.get("lead_score")
            interest = filters.get("interest")
            last_contacted = filters.get("last_contacted")
            if budget:
                qs = qs.filter(budget__lte=budget)
            if city:
                qs = qs.filter(city__icontains=city)
            if builder:
                qs = qs.filter(builder__icontains=builder)
            if configuration:
                qs = qs.filter(configuration__icontains=configuration)
            if occupation:
                qs = qs.filter(occupation__icontains=occupation)
            if lead_score:
                qs = qs.filter(lead_score__gte=lead_score)
            if interest:
                qs = qs.filter(interest__icontains=interest)
        return qs

    @staticmethod
    def get_delivery_stats(campaign):
        messages = CampaignMessage.objects.filter(campaign=campaign)
        total = messages.count()
        delivered = messages.filter(status__in=["DELIVERED", "OPENED", "CLICKED", "REPLIED"]).count()
        opened = messages.filter(status__in=["OPENED", "CLICKED", "REPLIED"]).count()
        clicked = messages.filter(status__in=["CLICKED", "REPLIED"]).count()
        replied = messages.filter(status="REPLIED").count()
        failed = messages.filter(status="FAILED").count()
        return {
            "total": total,
            "delivered": delivered,
            "opened": opened,
            "clicked": clicked,
            "replied": replied,
            "failed": failed,
            "delivery_rate": round((delivered / total) * 100, 1) if total > 0 else 0,
            "open_rate": round((opened / delivered) * 100, 1) if delivered > 0 else 0,
            "click_rate": round((clicked / opened) * 100, 1) if opened > 0 else 0,
            "reply_rate": round((replied / opened) * 100, 1) if opened > 0 else 0,
        }