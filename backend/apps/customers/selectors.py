from django.db import models
from apps.customers.models import Customer, CustomerTimelineEvent


class CustomerSelector:
    @staticmethod
    def list_customers(organization, search_query=None):
        queryset = Customer.objects.filter(organization=organization)
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query)
                | models.Q(last_name__icontains=search_query)
                | models.Q(email__icontains=search_query)
                | models.Q(phone__icontains=search_query)
            )
        return queryset

    @staticmethod
    def list_timeline_events(organization, customer_id):
        return CustomerTimelineEvent.objects.filter(
            organization=organization, customer_id=customer_id
        )
