from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.chat_service import chat_with_project_context
from config.logger import logger

router = APIRouter()


class ProjectChatRequest(BaseModel):
    session_id: str
    message: str
    context: dict = {}


class ProjectChatResponse(BaseModel):
    response: str


@router.post("/project-chat/", response_model=ProjectChatResponse)
async def project_chat(request: ProjectChatRequest):
    try:
        logger.info(f"Project chat request - Session: {request.session_id}")
        reply = await chat_with_project_context(
            str(request.session_id),
            request.message,
            request.context,
        )
        return {"response": reply}
    except Exception as e:
        logger.error(f"Project chat failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")
