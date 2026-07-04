from apps.documents.models import Document


class DocumentSelector:
    @staticmethod
    def list_documents(organization):
        return Document.objects.filter(organization=organization)

    @staticmethod
    def get_document_by_id(organization, document_id):
        return Document.objects.get(organization=organization, id=document_id)
