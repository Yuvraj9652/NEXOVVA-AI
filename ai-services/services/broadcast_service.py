from fastapi import HTTPException

from config.prompts import (
    BROADCAST_AUDIENCE_MATCH_PROMPT,
    BROADCAST_CONTENT_PROMPT,
    BROADCAST_PERSONALIZE_PROMPT,
    BROADCAST_SCHEDULE_PROMPT,
    BROADCAST_FOLLOWUP_PROMPT,
)
from llm.router import generate_text, generate_json
from config.logger import logger


async def audience_match(campaign_id: int, query: str, filters: dict = None):
    try:
        prompt = BROADCAST_AUDIENCE_MATCH_PROMPT.format(
            campaign_id=campaign_id,
            query=query,
            filters=str(filters or {}),
        )
        result = await generate_json(prompt)
        return {
            "segment_id": f"seg_{campaign_id}_{hash(query) % 10000}",
            "segment_name": f"AI Match: {query[:50]}",
            "query": query,
            "customer_count": result.get("customer_count", 0),
            "filters": filters or {},
        }
    except Exception as e:
        logger.error(f"Audience match failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def generate_broadcast_content(campaign_id: int, content_type: str, audience_segment: str = ""):
    try:
        prompt = BROADCAST_CONTENT_PROMPT.format(
            campaign_id=campaign_id,
            content_type=content_type,
            audience_segment=audience_segment,
        )
        result = await generate_text(prompt)
        return {
            "content_type": content_type,
            "content": result,
            "campaign_id": campaign_id,
        }
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def personalize_broadcast_message(campaign_id: int, customer_name: str, customer_phone: str, customer_email: str, content_type: str):
    try:
        prompt = BROADCAST_PERSONALIZE_PROMPT.format(
            campaign_id=campaign_id,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            content_type=content_type,
        )
        result = await generate_text(prompt)
        return {
            "customer_name": customer_name,
            "content_type": content_type,
            "personalized_message": result,
        }
    except Exception as e:
        logger.error(f"Personalize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def optimize_broadcast_schedule(campaign_id: int, audience_size: int):
    try:
        prompt = BROADCAST_SCHEDULE_PROMPT.format(
            campaign_id=campaign_id,
            audience_size=audience_size,
        )
        result = await generate_json(prompt)
        return {
            "campaign_id": campaign_id,
            "recommendations": result,
        }
    except Exception as e:
        logger.error(f"Schedule optimize failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def check_duplicate_broadcast(campaign_id: int, customer_phone: str, customer_email: str = ""):
    try:
        prompt = BROADCAST_DUPLICATE_PROMPT.format(
            campaign_id=campaign_id,
            customer_phone=customer_phone,
            customer_email=customer_email,
        )
        result = await generate_json(prompt)
        return {
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "is_duplicate": result.get("is_duplicate", False),
            "campaign_id": campaign_id,
        }
    except Exception as e:
        logger.error(f"Duplicate check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def suggest_follow_up(campaign_id: int, customer_id: int, message_status: str, days_since_sent: int):
    try:
        prompt = BROADCAST_FOLLOWUP_PROMPT.format(
            campaign_id=campaign_id,
            customer_id=customer_id,
            message_status=message_status,
            days_since_sent=days_since_sent,
        )
        result = await generate_json(prompt)
        return {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "follow_up_action": result,
        }
    except Exception as e:
        logger.error(f"Follow-up suggestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))