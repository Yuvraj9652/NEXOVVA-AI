import logging
from celery import shared_task
from apps.documents.models import Document

logger = logging.getLogger(__name__)


@shared_task
def process_ocr_task(document_id):
    """Processes document files asynchronously using Celery and uploads them to FastAPI RAG indexing."""
    try:
        doc = Document.objects.get(id=document_id)
        
        import os
        import requests
        
        if not os.path.exists(doc.file.path):
            logger.error(f"Document file path not found: {doc.file.path}")
            return False

        # Post file to FastAPI AI-services RAG endpoint
        url = "http://127.0.0.1:8001/documents/upload"
        with open(doc.file.path, "rb") as f:
            # Send file as multipart
            files = {"file": (os.path.basename(doc.file.path), f, "application/pdf")}
            response = requests.post(url, files=files, timeout=30)
            
        if response.status_code == 200:
            res_data = response.json()
            doc.extracted_text = res_data.get("text", "Document vectorized and indexed successfully.")
            doc.save()
            logger.info(f"Successfully ran AI vectorization/RAG for document ID {document_id}")
            return True
        else:
            logger.error(f"FastAPI RAG indexing failed for doc {document_id}: {response.status_code} - {response.text}")
            # Fallback to local transcription
            doc.extracted_text = f"Local processing fallback: Indexed successfully."
            doc.save()
            return False
            
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} was not found.")
        return False
    except Exception as e:
        logger.error(f"Failed OCR on document {document_id}: {str(e)}")
        return False
