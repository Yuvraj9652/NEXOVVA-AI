from fastapi import APIRouter

from api.schemas import (
    RecommendationRequest,
    RecommendationResponse,
)

from services.recommendation_service import recommend_property

router = APIRouter(
    prefix="/recommend-property",
    tags=["Recommendation AI"],
)


@router.post("/", response_model=RecommendationResponse)
async def recommendation(request: RecommendationRequest):

    result = await recommend_property(
        budget=request.budget,
        city=request.city,
        family_size=request.family_size,
        property_type=request.property_type,
        preferences=request.preferences,
    )

    return RecommendationResponse(**result)