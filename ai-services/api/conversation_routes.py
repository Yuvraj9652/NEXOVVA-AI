from fastapi import APIRouter
from services.conversation_service import conversation_store

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


@router.delete("/{session_id}")
async def clear_conversation(session_id: str):
    conversation_store.pop(session_id, None)

    return {
        "message": "Conversation cleared."
    }