from apps.customers.models import Customer
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.leads.models import Lead
from apps.pipeline.models import Deal
from apps.tasks.models import Task
from apps.properties.models import Unit
from apps.employees.models import Employee

from apps.contacts.serializers import ContactSerializer
from apps.pipeline.serializers import DealSerializer
from apps.tasks.serializers import TasksSerializer
from apps.ai.selectors import AISelector


class DashboardService:
    @staticmethod
    def get_summary(organization):
        contacts_qs = Contact.objects.filter(organization=organization).select_related("assigned_to")
        deals_qs = Deal.objects.filter(organization=organization).select_related("stage", "assigned_to", "contact", "company")
        tasks_qs = Task.objects.filter(organization=organization).select_related("assigned_to", "contact", "deal", "lead")
        
        ai_usage = AISelector.get_usage_analytics(organization=organization)

        return {
            "contacts": ContactSerializer(contacts_qs, many=True).data,
            "deals": DealSerializer(deals_qs, many=True).data,
            "tasks": TasksSerializer(tasks_qs, many=True).data,
            "aiUsage": ai_usage,
            "stats": {
                "customers": Customer.objects.filter(organization=organization).count(),
                "contacts": Contact.objects.filter(organization=organization).count(),
                "companies": Company.objects.filter(organization=organization).count(),
                "leads": Lead.objects.filter(organization=organization).count(),
                "deals": Deal.objects.filter(organization=organization).count(),
                "tasks": Task.objects.filter(organization=organization).count(),
                "properties": Unit.objects.filter(organization=organization).count(),
                "employees": Employee.objects.filter(organization=organization).count(),
            }
        }