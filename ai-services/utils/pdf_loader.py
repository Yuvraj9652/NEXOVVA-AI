from pypdf import PdfReader


def load_pdf(path: str) -> str:
    reader = PdfReader(path)

    text = ""

    for page_no, page in enumerate(reader.pages):
        extracted = page.extract_text()

        if extracted:
            text += extracted + "\n"

    return text.strip()