from django.db import transaction
from apps.customers.models import Customer, CustomerTimelineEvent


class CustomerService:
    @staticmethod
    @transaction.atomic
    def create_customer(
        organization, first_name, last_name, email, phone="", segment=Customer.Segments.CLIENT
    ):
        customer = Customer.objects.create(
            organization=organization,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            segment=segment,
        )
        return customer

    @staticmethod
    @transaction.atomic
    def log_timeline_event(organization, customer_id, event_type, description):
        customer = Customer.objects.get(organization=organization, id=customer_id)
        event = CustomerTimelineEvent.objects.create(
            organization=organization,
            customer=customer,
            event_type=event_type,
            description=description,
        )
        return event
