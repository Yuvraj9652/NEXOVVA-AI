import logging
from celery import shared_task
from apps.documents.models import Document

logger = logging.getLogger(__name__)


@shared_task
def process_ocr_task(document_id):
    """Processes document files asynchronously using Celery and uploads them to FastAPI RAG indexing."""
    try:
        doc = Document.objects.get(id=document_id)
        
        # 1. Update status to Extracting
        doc.status = Document.Statuses.EXTRACTING
        doc.save()
        
        import os
        import requests
        import mimetypes
        from django.conf import settings
        from urllib.parse import urljoin
        
        if not os.path.exists(doc.file.path):
            logger.error(f"Document file path not found: {doc.file.path}")
            doc.status = Document.Statuses.FAILED
            doc.save()
            return False

        # Guess mime type dynamically
        mime_type, _ = mimetypes.guess_type(doc.file.path)
        if not mime_type:
            mime_type = "application/octet-stream"

        # 2. Update status to Embedding
        doc.status = Document.Statuses.EMBEDDING
        doc.save()

        # Post file to FastAPI AI-services RAG endpoint
        url = urljoin(settings.AI_SERVICE_URL, "/documents/upload")
        with open(doc.file.path, "rb") as f:
            # Send file as multipart with dynamic mime type and organization ID
            files = {"file": (os.path.basename(doc.file.path), f, mime_type)}
            data = {"organization_id": str(doc.organization.id)}
            response = requests.post(url, files=files, data=data, timeout=60)
            
        if response.status_code == 200:
            res_data = response.json()
            doc.extracted_text = res_data.get("text", "Document vectorized and indexed successfully.")
            doc.status = Document.Statuses.READY
            doc.save()
            logger.info(f"Successfully ran AI vectorization/RAG for document ID {document_id}")
            return True
        else:
            logger.error(f"FastAPI RAG indexing failed for doc {document_id}: {response.status_code} - {response.text}")
            doc.status = Document.Statuses.FAILED
            doc.save()
            return False
            
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} was not found.")
        return False
    except Exception as e:
        logger.error(f"Failed OCR on document {document_id}: {str(e)}")
        try:
            doc = Document.objects.get(id=document_id)
            doc.status = Document.Statuses.FAILED
            doc.save()
        except Exception:
            pass
        return False


@shared_task
def delete_document_vector_task(filename, organization_id):
    """Deletes document chunks from ChromaDB vectorstore via FastAPI."""
    try:
        import requests
        from django.conf import settings
        from urllib.parse import urljoin
        
        url = urljoin(settings.AI_SERVICE_URL, "/documents/delete")
        response = requests.delete(
            url,
            params={
                "filename": filename,
                "organization_id": str(organization_id)
            },
            timeout=30
        )
        if response.status_code == 200:
            logger.info(f"Successfully deleted vectorstore entries for document '{filename}' (Org {organization_id})")
            return True
        else:
            logger.error(f"Failed to delete vectorstore entries for document '{filename}': {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error in delete_document_vector_task: {str(e)}")
        return False

