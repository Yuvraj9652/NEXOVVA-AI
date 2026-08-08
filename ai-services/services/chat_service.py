from fastapi import HTTPException

from config.prompts import CHAT_SYSTEM_PROMPT, PROJECT_CHAT_SYSTEM_PROMPT
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


async def chat_with_project_context(session_id: str, message: str, context: dict):
    try:
        history = get_history(session_id)
        history_text = ""
        for item in history:
            history_text += f"{item['role']}: {item['content']}\n"

        project_info = f"""
Project Name: {context.get('project_name', 'N/A')}
Builder: {context.get('builder', 'N/A')}
City: {context.get('city', 'N/A')}
Status: {context.get('status', 'N/A')}
Property Type: {context.get('property_type', 'N/A')}
Price Range: {context.get('starting_price', 'N/A')} - {context.get('max_price', 'N/A')}
Configurations: {', '.join(context.get('configurations', []))}
Amenities: {', '.join(context.get('amenities', []))}
Highlights: {', '.join(context.get('highlights', []))}
RERA Number: {context.get('rera_number', 'N/A')}
Possession Date: {context.get('possession_date', 'N/A')}
Description: {context.get('description', 'N/A')}
"""

        prompt = f"""
{PROJECT_CHAT_SYSTEM_PROMPT}

Project Information:

{project_info}

Conversation History:

{history_text}

User Question:

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
