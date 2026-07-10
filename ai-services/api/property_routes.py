from fastapi import APIRouter

from api.schemas import (
    PropertyDescriptionRequest,
    PropertyDescriptionResponse,
)

from services.property_service import generate_property_description

router = APIRouter(
    prefix="/property-description",
    tags=["Property AI"],
)


@router.post("/", response_model=PropertyDescriptionResponse)
async def property_description(
    request: PropertyDescriptionRequest,
):
    description = await generate_property_description(
        property_type=request.property_type,
        city=request.city,
        bedrooms=request.bedrooms,
        bathrooms=request.bathrooms,
        price=request.price,
        features=request.features,
    )

    return PropertyDescriptionResponse(
        description=description
    )