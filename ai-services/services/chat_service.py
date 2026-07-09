from fastapi import HTTPException

from config.prompts import CHAT_SYSTEM_PROMPT
from llm.router import generate_text
from services.conversation_service import (
    get_history,
    add_message,
)


async def chat(session_id: str, message: str):
    try:

        history = get_history(session_id)

        history_text = ""

        for item in history:
            history_text += f"{item['role']}: {item['content']}\n"

        prompt = f"""
{CHAT_SYSTEM_PROMPT}

Conversation History:

{history_text}

User:

{message}
"""

        reply = await generate_text(prompt)

        add_message(session_id, "user", message)
        add_message(session_id, "assistant", reply)

        return reply

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )