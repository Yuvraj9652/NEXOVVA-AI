from pathlib import Path
import traceback

from fastapi import APIRouter, File, UploadFile, HTTPException, Form

from api.schemas import AskDocumentRequest
from services.rag_service import (
    upload_document,
    ask_document,
)
from services.vector_db import collection

router = APIRouter(
    prefix="/documents",
    tags=["RAG AI"]
)

UPLOAD_FOLDER = Path("uploads/brochures")
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...), organization_id: str = Form("default")):
    try:

        file_path = UPLOAD_FOLDER / file.filename

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return await upload_document(
            str(file_path),
            file.filename,
            organization_id
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
        request.question,
        request.organization_id
    )


@router.delete("/delete")
async def delete_document(filename: str, organization_id: str):
    try:
        collection.delete(where={
            "$and": [
                {"filename": filename},
                {"organization_id": organization_id}
            ]
        })
        return {
            "status": "success",
            "message": f"Successfully deleted document '{filename}' from ChromaDB."
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )