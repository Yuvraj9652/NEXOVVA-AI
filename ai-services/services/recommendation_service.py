from fastapi import HTTPException

from config.prompts import RECOMMENDATION_PROMPT_TEMPLATE
from llm.router import generate_json


async def recommend_property(
    budget: str,
    city: str,
    family_size: int,
    property_type: str,
    preferences: list[str],
):
    try:

        prompt = RECOMMENDATION_PROMPT_TEMPLATE.format(
            budget=budget,
            city=city,
            family_size=family_size,
            property_type=property_type,
            preferences=", ".join(preferences),
        )

        return await generate_json(prompt)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )