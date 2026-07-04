from django.db import transaction
from apps.documents.models import Document


class DocumentService:
    @staticmethod
    @transaction.atomic
    def upload_document(organization, name, file):
        doc = Document.objects.create(
            organization=organization,
            name=name,
            file=file,
        )

        # Trigger background OCR processing
        from apps.documents.tasks import process_ocr_task
        transaction.on_commit(lambda: process_ocr_task.delay(doc.id))
        return doc

    @staticmethod
    @transaction.atomic
    def update_document_text(organization, document_id, text):
        doc = Document.objects.get(organization=organization, id=document_id)
        doc.extracted_text = text
        doc.version += 1
        doc.save()
        return doc
