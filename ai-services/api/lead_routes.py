from fastapi import APIRouter

from api.schemas import LeadScoreRequest, LeadScoreResponse
from services.lead_service import generate_lead_score

router = APIRouter(
    prefix="/lead-score",
    tags=["Lead AI"],
)


@router.post("/", response_model=LeadScoreResponse)
async def lead_score(request: LeadScoreRequest):

    result = await generate_lead_score(
        customer_name=request.customer_name,
        budget=request.budget,
        timeline=request.timeline,
        interest_level=request.interest_level,
        property_type=request.property_type,
    )

    return LeadScoreResponse(**result)