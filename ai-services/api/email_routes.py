from fastapi import APIRouter

from api.schemas import EmailRequest, EmailResponse
from services.email_service import generate_email

router = APIRouter(
    prefix="/generate-email",
    tags=["Email AI"],
)


@router.post("/", response_model=EmailResponse)
async def email_generator(request: EmailRequest):

    email = await generate_email(
        customer_name=request.customer_name,
        property_name=request.property_name,
        property_type=request.property_type,
        city=request.city,
        budget=request.budget,
    )

    return EmailResponse(email=email)