import csv
import os
import zipfile
import xml.etree.ElementTree as ET
from utils.pdf_loader import load_pdf
from config.logger import logger


def load_csv(path: str, filename: str) -> str:
    """
    Parses a CSV file and converts each row into a descriptive textual line
    suitable for embedding generation and semantic similarity search.
    """
    lines = []
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if not headers:
                return ""
            
            # Clean headers
            headers = [h.strip() for h in headers if h.strip()]
            for row_idx, row in enumerate(reader):
                row_parts = []
                for col_idx, val in enumerate(row):
                    if col_idx < len(headers):
                        header = headers[col_idx]
                        row_parts.append(f"{header} is {val.strip()}")
                    else:
                        row_parts.append(f"Column_{col_idx} is {val.strip()}")
                if row_parts:
                    lines.append(f"In {filename}, row {row_idx + 1}: " + ", ".join(row_parts) + ".")
    except Exception as e:
        logger.error(f"Error parsing CSV: {e}")
        raise ValueError(f"Failed to parse CSV: {str(e)}")
    return "\n".join(lines)


def load_docx(path: str) -> str:
    """
    Parses a DOCX file and extracts text natively without external dependencies.
    """
    try:
        texts = []
        with zipfile.ZipFile(path) as docx:
            xml_content = docx.read('word/document.xml')
            root = ET.fromstring(xml_content)
            
            # Find all paragraph elements and extract text
            for paragraph in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
                p_text = []
                for run in paragraph.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                    if run.text:
                        p_text.append(run.text)
                if p_text:
                    texts.append("".join(p_text))
        return "\n".join(texts).strip()
    except Exception as e:
        logger.error(f"Error parsing DOCX: {e}")
        raise ValueError(f"Failed to parse DOCX file: {str(e)}")


def load_document(file_path: str) -> str:
    """
    Dispatcher to load document text based on file extension.
    Supports PDF, DOCX, TXT, CSV and provides a generic fallback.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Check empty files
    if os.path.getsize(file_path) == 0:
        raise ValueError("Uploaded file is empty.")

    _, ext = os.path.splitext(file_path.lower())
    filename = os.path.basename(file_path)

    if ext == ".pdf":
        return load_pdf(file_path)
    elif ext == ".docx":
        return load_docx(file_path)
    elif ext in [".txt", ".log"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except Exception as e:
            raise ValueError(f"Failed to read TXT file: {str(e)}")
    elif ext == ".csv":
        return load_csv(file_path, filename)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

