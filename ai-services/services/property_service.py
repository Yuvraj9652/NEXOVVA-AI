from fastapi import HTTPException

from config.prompts import PROPERTY_PROMPT_TEMPLATE
from llm.router import generate_text


async def generate_property_description(
    property_type: str,
    city: str,
    bedrooms: int,
    bathrooms: int,
    price: str,
    features: list[str],
):
    try:
        prompt = PROPERTY_PROMPT_TEMPLATE.format(
            property_type=property_type,
            city=city,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            price=price,
            features=", ".join(features),
        )

        return await generate_text(prompt)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )