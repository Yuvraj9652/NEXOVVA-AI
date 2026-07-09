from fastapi import HTTPException

from config.prompts import MEETING_SUMMARY_PROMPT_TEMPLATE
from llm.router import generate_json


async def generate_meeting_summary(transcript: str):
    try:
        prompt = MEETING_SUMMARY_PROMPT_TEMPLATE.format(
            transcript=transcript
        )

        return await generate_json(prompt)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )