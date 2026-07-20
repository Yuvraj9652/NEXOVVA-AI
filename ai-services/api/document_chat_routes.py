from fastapi import APIRouter
from pydantic import BaseModel

from services.document_chat_service import chat_with_document

router = APIRouter(
    prefix="/document-chat",
    tags=["Document Chat"]
)


class DocumentChatRequest(BaseModel):
    session_id: str
    filename: str
    question: str


@router.post("/")
async def document_chat(request: DocumentChatRequest):

    return await chat_with_document(
        request.session_id,
        request.filename,
        request.question
    )