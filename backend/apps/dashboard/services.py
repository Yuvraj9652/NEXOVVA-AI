from apps.customers.models import Customer
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.leads.models import Lead
from apps.pipeline.models import Deal
from apps.tasks.models import Task
from apps.properties.models import Unit
from apps.employees.models import Employee


class DashboardService:
    @staticmethod
    def get_summary(organization):
        return {
            "customers": Customer.objects.filter(organization=organization).count(),
            "contacts": Contact.objects.filter(organization=organization).count(),
            "companies": Company.objects.filter(organization=organization).count(),
            "leads": Lead.objects.filter(organization=organization).count(),
            "deals": Deal.objects.filter(organization=organization).count(),
            "tasks": Task.objects.filter(organization=organization).count(),
            "properties": Unit.objects.filter(organization=organization).count(),
            "employees": Employee.objects.filter(organization=organization).count(),
        }