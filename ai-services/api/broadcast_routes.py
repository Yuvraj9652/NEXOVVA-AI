from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config.prompts import (
    BROADCAST_AUDIENCE_MATCH_PROMPT,
    BROADCAST_CONTENT_PROMPT,
    BROADCAST_PERSONALIZE_PROMPT,
    BROADCAST_SCHEDULE_PROMPT,
    BROADCAST_FOLLOWUP_PROMPT,
)
from config.logger import logger
from services.broadcast_service import (
    audience_match,
    generate_broadcast_content,
    personalize_broadcast_message,
    optimize_broadcast_schedule,
    check_duplicate_broadcast,
    suggest_follow_up,
)

router = APIRouter()


class AudienceMatchRequest(BaseModel):
    campaign_id: int
    query: str
    filters: dict = {}


class AudienceMatchResponse(BaseModel):
    segment_id: str
    segment_name: str
    query: str
    customer_count: int
    filters: dict


@router.post("/audience-match", response_model=AudienceMatchResponse)
async def ai_audience_match(request: AudienceMatchRequest):
    try:
        logger.info(f"AI audience match - Campaign: {request.campaign_id}, Query: {request.query}")
        result = await audience_match(
            campaign_id=request.campaign_id,
            query=request.query,
            filters=request.filters,
        )
        return result
    except Exception as e:
        logger.error(f"AI audience match failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class ContentGenerateRequest(BaseModel):
    campaign_id: int
    content_type: str
    audience_segment: str = ""


class ContentGenerateResponse(BaseModel):
    content_type: str
    content: str
    campaign_id: int


@router.post("/generate-content", response_model=ContentGenerateResponse)
async def ai_generate_content(request: ContentGenerateRequest):
    try:
        logger.info(f"AI content generation - Campaign: {request.campaign_id}, Type: {request.content_type}")
        result = await generate_broadcast_content(
            campaign_id=request.campaign_id,
            content_type=request.content_type,
            audience_segment=request.audience_segment,
        )
        return result
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class PersonalizeRequest(BaseModel):
    campaign_id: int
    customer_name: str
    customer_phone: str = ""
    customer_email: str = ""
    content_type: str


class PersonalizeResponse(BaseModel):
    customer_name: str
    content_type: str
    personalized_message: str


@router.post("/personalize", response_model=PersonalizeResponse)
async def ai_personalize(request: PersonalizeRequest):
    try:
        logger.info(f"AI personalize - Campaign: {request.campaign_id}, Customer: {request.customer_name}")
        result = await personalize_broadcast_message(
            campaign_id=request.campaign_id,
            customer_name=request.customer_name,
            customer_phone=request.customer_phone,
            customer_email=request.customer_email,
            content_type=request.content_type,
        )
        return result
    except Exception as e:
        logger.error(f"AI personalize failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class ScheduleOptimizeRequest(BaseModel):
    campaign_id: int
    audience_size: int = 100


class ScheduleOptimizeResponse(BaseModel):
    campaign_id: int
    recommendations: dict


@router.post("/optimize-schedule", response_model=ScheduleOptimizeResponse)
async def ai_optimize_schedule(request: ScheduleOptimizeRequest):
    try:
        logger.info(f"AI schedule optimize - Campaign: {request.campaign_id}")
        result = await optimize_broadcast_schedule(
            campaign_id=request.campaign_id,
            audience_size=request.audience_size,
        )
        return result
    except Exception as e:
        logger.error(f"AI schedule optimize failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class DuplicateCheckRequest(BaseModel):
    campaign_id: int
    customer_phone: str
    customer_email: str = ""


class DuplicateCheckResponse(BaseModel):
    customer_phone: str
    customer_email: str
    is_duplicate: bool
    campaign_id: int


@router.post("/check-duplicate", response_model=DuplicateCheckResponse)
async def ai_check_duplicate(request: DuplicateCheckRequest):
    try:
        logger.info(f"AI duplicate check - Campaign: {request.campaign_id}, Phone: {request.customer_phone}")
        result = await check_duplicate_broadcast(
            campaign_id=request.campaign_id,
            customer_phone=request.customer_phone,
            customer_email=request.customer_email,
        )
        return result
    except Exception as e:
        logger.error(f"AI duplicate check failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")


class FollowUpRequest(BaseModel):
    campaign_id: int
    customer_id: int
    message_status: str
    days_since_sent: int = 0


class FollowUpResponse(BaseModel):
    campaign_id: int
    customer_id: int
    follow_up_action: dict


@router.post("/follow-up", response_model=FollowUpResponse)
async def ai_follow_up(request: FollowUpRequest):
    try:
        logger.info(f"AI follow-up - Campaign: {request.campaign_id}, Customer: {request.customer_id}")
        result = await suggest_follow_up(
            campaign_id=request.campaign_id,
            customer_id=request.customer_id,
            message_status=request.message_status,
            days_since_sent=request.days_since_sent,
        )
        return result
    except Exception as e:
        logger.error(f"AI follow-up failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")