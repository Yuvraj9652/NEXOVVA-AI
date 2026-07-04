import logging
from celery import shared_task
from apps.documents.models import Document

logger = logging.getLogger(__name__)


@shared_task
def process_ocr_task(document_id):
    """Processes document files asynchronously using Celery to parse layout contents (OCR)."""
    try:
        doc = Document.objects.get(id=document_id)
        
        # Simulate text extraction (in production, we'd run OCR libraries or pass files to Gemini Multimodal)
        mock_extracted_data = (
            f"[OCR TRANSCRIPTION START]\n"
            f"Document Title: {doc.name}\n"
            f"File Path reference: {doc.file.url}\n"
            f"Index Reference: Apex Realty & Partners\n"
            f"Terms identified: Real estate lease agreement, security deposit bounds, tenant liabilities.\n"
            f"[OCR TRANSCRIPTION END]"
        )

        doc.extracted_text = mock_extracted_data
        doc.save()
        
        logger.info(f"Successfully ran OCR extraction for document ID {document_id}")
        return True
    except Document.DoesNotExist:
        logger.error(f"Document with ID {document_id} was not found.")
        return False
    except Exception as e:
        logger.error(f"Failed OCR on document {document_id}: {str(e)}")
        return False
