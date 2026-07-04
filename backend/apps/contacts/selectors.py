from django.db import models
from apps.contacts.models import Contact


class ContactSelector:
    @staticmethod
    def list_contacts(organization, search_query=None, status=None):
        queryset = Contact.objects.filter(organization=organization).select_related("assigned_to")
        if status:
            queryset = queryset.filter(status=status)
        if search_query:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search_query)
                | models.Q(last_name__icontains=search_query)
                | models.Q(email__icontains=search_query)
                | models.Q(phone__icontains=search_query)
            )
        return queryset

    @staticmethod
    def get_contact_by_id(organization, contact_id):
        return Contact.objects.select_related("assigned_to").get(
            organization=organization, id=contact_id
        )
