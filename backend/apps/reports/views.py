from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Sum, Count

from apps.authentication.permissions import IsOrganizationMember, IsManagerUserRole
from apps.contacts.models import Contact
from apps.leads.models import Lead
from apps.pipeline.models import Deal
from apps.tasks.models import Task
from apps.ai.models import AIUsage


class ReportsSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsManagerUserRole]

    def get(self, request):
        org = request.organization

        # Aggregate counts
        contacts_count = Contact.objects.filter(organization=org).count()
        leads_count = Lead.objects.filter(organization=org).count()
        
        deals_agg = Deal.objects.filter(organization=org).aggregate(
            total_value=Sum("amount"),
            count=Count("id")
        )
        
        tasks_total = Task.objects.filter(organization=org).count()
        tasks_completed = Task.objects.filter(organization=org, completed=True).count()
        task_ratio = (tasks_completed / tasks_total * 100) if tasks_total > 0 else 0

        ai_agg = AIUsage.objects.filter(organization=org).aggregate(
            total_cost=Sum("cost"),
            total_requests=Count("id")
        )

        # Stage distribution
        deals = Deal.objects.filter(organization=org).select_related("stage")
        stage_dist = {}
        for d in deals:
            name = d.stage.name
            stage_dist[name] = stage_dist.get(name, 0.0) + float(d.amount)

        data = {
            "contacts_count": contacts_count,
            "leads_count": leads_count,
            "pipeline_total_value": float(deals_agg["total_value"] or 0.0),
            "pipeline_deals_count": deals_agg["count"] or 0,
            "tasks_completion_ratio": round(task_ratio, 2),
            "ai_total_cost": float(ai_agg["total_cost"] or 0.0),
            "ai_total_requests": ai_agg["total_requests"] or 0,
            "stage_distribution": stage_dist,
        }

        return Response(data)
