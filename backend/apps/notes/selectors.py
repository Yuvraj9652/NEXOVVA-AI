from apps.notes.models import Note


class NotesSelector:
    @staticmethod
    def list_notes(organization, contact_id=None, deal_id=None, lead_id=None):
        queryset = Note.objects.filter(organization=organization).select_related("author")
        if contact_id:
            queryset = queryset.filter(contact_id=contact_id)
        if deal_id:
            queryset = queryset.filter(deal_id=deal_id)
        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)
        return queryset

    @staticmethod
    def get_note_by_id(organization, note_id):
        return Note.objects.select_related("author").get(organization=organization, id=note_id)
