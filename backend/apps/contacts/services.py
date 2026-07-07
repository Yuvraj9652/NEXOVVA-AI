from django.db import transaction
from django.contrib.auth import get_user_model
from apps.contacts.models import Contact
from apps.audit.services import ActivityLogService

User = get_user_model()

class ContactService:
    @staticmethod
    @transaction.atomic
    def create_contact(
        organization,
        user,
        first_name,
        last_name,
        email,
        phone="",
        status=Contact.Statuses.ACTIVE,
        assigned_to_id=None,
    ):
        assigned_to = None
        if assigned_to_id:
            assigned_to = User.objects.get(id=assigned_to_id)

        contact = Contact.objects.create(
            organization=organization,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            status=status,
            assigned_to=assigned_to,
        )

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="contact_created",
            target_type="contact",
            target_id=contact.id,
            description=f"Contact '{contact.first_name} {contact.last_name}' was created.",
        )
        return contact

    @staticmethod
    @transaction.atomic
    def update_contact(organization, user, contact_id, **fields):
        contact = Contact.objects.get(organization=organization, id=contact_id)

        # Track fields to update
        for field, value in fields.items():
            if field == "assigned_to_id":
                contact.assigned_to = User.objects.get(id=value) if value else None
            elif hasattr(contact, field):
                setattr(contact, field, value)

        contact.save()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="contact_updated",
            target_type="contact",
            target_id=contact.id,
            description=f"Contact '{contact.first_name} {contact.last_name}' was updated.",
        )
        return contact

    @staticmethod
    @transaction.atomic
    def delete_contact(organization, user, contact_id):
        contact = Contact.objects.get(organization=organization, id=contact_id)
        name = f"{contact.first_name} {contact.last_name}"
        contact.delete()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="contact_deleted",
            target_type="contact",
            target_id=contact_id,
            description=f"Contact '{name}' was deleted.",
        )
        return True
