from django.db import transaction
from apps.notes.models import Note
from apps.contacts.models import Contact
from apps.pipeline.models import Deal
from apps.leads.models import Lead


class NotesService:
    @staticmethod
    @transaction.atomic
    def create_note(
        organization, author, content, contact_id=None, deal_id=None, lead_id=None
    ):
        contact = Contact.objects.get(organization=organization, id=contact_id) if contact_id else None
        deal = Deal.objects.get(organization=organization, id=deal_id) if deal_id else None
        lead = Lead.objects.get(organization=organization, id=lead_id) if lead_id else None

        note = Note.objects.create(
            organization=organization,
            author=author,
            content=content,
            contact=contact,
            deal=deal,
            lead=lead,
        )
        return note

    @staticmethod
    @transaction.atomic
    def update_note(organization, author, note_id, content):
        # Only authors or Admins/Managers should be allowed to edit, checked at View level
        note = Note.objects.get(organization=organization, id=note_id)
        note.content = content
        note.save()
        return note

    @staticmethod
    @transaction.atomic
    def delete_note(organization, author, note_id):
        note = Note.objects.get(organization=organization, id=note_id)
        note.delete()
        return True
