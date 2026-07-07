from django.db.models import Sum

from apps.customers.models import Customer
from apps.leads.models import Lead
from apps.pipeline.models import Deal
from apps.tasks.models import Task
from apps.properties.models import Unit


class AnalyticsService:
    @staticmethod
    def get_analytics(organization):
        total_revenue = (
            Deal.objects.filter(organization=organization)
            .aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return {
            "total_revenue": total_revenue,
            "total_customers": Customer.objects.filter(
                organization=organization
            ).count(),
            "active_leads": Lead.objects.filter(
                organization=organization
            ).count(),
            "won_deals": Deal.objects.filter(
                organization=organization
            ).count(),
            "completed_tasks": Task.objects.filter(
                organization=organization,
                completed=True,
            ).count(),
            "total_properties": Unit.objects.filter(
                organization=organization
            ).count(),
        }