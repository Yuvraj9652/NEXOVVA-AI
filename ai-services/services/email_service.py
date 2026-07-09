from fastapi import HTTPException

from config.prompts import EMAIL_PROMPT_TEMPLATE
from llm.router import generate_text


async def generate_email(
    customer_name: str,
    property_name: str,
    property_type: str,
    city: str,
    budget: str,
):
    try:
        prompt = EMAIL_PROMPT_TEMPLATE.format(
            customer_name=customer_name,
            property_name=property_name,
            property_type=property_type,
            city=city,
            budget=budget,
        )

        return await generate_text(prompt)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )