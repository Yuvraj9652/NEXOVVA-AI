from fastapi import APIRouter

from api.schemas import ChatRequest, ChatResponse
from services.chat_service import chat

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post("/", response_model=ChatResponse)
async def chat_route(request: ChatRequest):
    reply = await chat(
        request.session_id,
        request.message,
    )

    return ChatResponse(response=reply)