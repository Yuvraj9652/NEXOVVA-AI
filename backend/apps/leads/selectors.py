from django.db import models
from apps.leads.models import Lead


class LeadSelector:
    @staticmethod
    def list_leads(organization, search_query=None, status=None):
        queryset = Lead.objects.filter(organization=organization).select_related("contact", "company")
        if status:
            queryset = queryset.filter(status=status)
        if search_query:
            queryset = queryset.filter(
                models.Q(title__icontains=search_query)
                | models.Q(contact__first_name__icontains=search_query)
                | models.Q(contact__last_name__icontains=search_query)
                | models.Q(company__name__icontains=search_query)
            )
        return queryset

    @staticmethod
    def get_lead_by_id(organization, lead_id):
        return Lead.objects.select_related("contact", "company").get(
            organization=organization, id=lead_id
        )
