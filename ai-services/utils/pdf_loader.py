from pypdf import PdfReader
from google.genai import types
from config.llm import client, MODEL_NAME
from config.logger import logger

def ocr_pdf_with_gemini(file_path: str) -> str:
    logger.info(f"Running Gemini OCR on scanned PDF: {file_path}")
    try:
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[
                types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type="application/pdf"
                ),
                "Perform OCR on this PDF. Extract and return all text contents of the document. Preserve layout and formatting where possible. Return only the extracted text, do not add introductory or explanatory notes."
            ]
        )
        if response and response.text:
            extracted = response.text.strip()
            logger.info(f"Successfully finished Gemini OCR. Extracted {len(extracted)} characters.")
            return extracted
        else:
            raise Exception("Gemini OCR returned empty response.")
    except Exception as e:
        logger.error(f"Gemini OCR failed: {e}")
        raise Exception(f"OCR failed to extract text from PDF: {str(e)}")


def load_pdf(path: str) -> str:
    reader = PdfReader(path)

    text = ""

    for page_no, page in enumerate(reader.pages):
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    cleaned_text = text.strip()
    
    # Scanned PDF check: if page count > 0 and extracted text is empty or very short (< 50 chars)
    if len(reader.pages) > 0 and len(cleaned_text) < 50:
        logger.info(f"Extracted text from {path} is very short ({len(cleaned_text)} chars). Triggering Gemini OCR...")
        return ocr_pdf_with_gemini(path)

    return cleaned_text