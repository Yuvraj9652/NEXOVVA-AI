from fastapi import HTTPException

from config.prompts import LEAD_SCORING_PROMPT_TEMPLATE
from llm.router import generate_json


async def generate_lead_score(
    customer_name: str,
    budget: str,
    timeline: str,
    interest_level: str,
    property_type: str,
):
    try:
        prompt = LEAD_SCORING_PROMPT_TEMPLATE.format(
            customer_name=customer_name,
            budget=budget,
            timeline=timeline,
            interest_level=interest_level,
            property_type=property_type,
        )

        return await generate_json(prompt)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )