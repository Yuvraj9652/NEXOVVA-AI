from pathlib import Path
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException

from api.schemas import AskDocumentRequest
from services.rag_service import (
    upload_document,
    ask_document,
)

router = APIRouter(
    prefix="/documents",
    tags=["RAG AI"]
)

UPLOAD_FOLDER = Path("uploads/brochures")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    try:

        file_path = UPLOAD_FOLDER / file.filename

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return await upload_document(
            str(file_path),
            file.filename
        )

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/ask")
async def ask(request: AskDocumentRequest):
    return await ask_document(
        request.filename,
        request.question
    )