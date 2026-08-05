from fastapi import HTTPException

from config.prompts import (
    PROPERTY_PROMPT_TEMPLATE,
    PROJECT_DESCRIPTION_PROMPT,
    PROJECT_FAQ_PROMPT,
    PROJECT_HIGHLIGHTS_PROMPT,
)
from llm.router import generate_text, generate_json


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
        raise HTTPException(status_code=500, detail=str(e))


async def generate_project_content(
    project_name: str,
    builder: str,
    city: str,
    status: str,
    property_type: str,
    starting_price: str,
    max_price: str,
    configurations: list = [],
    amenities: list = [],
    highlights: list = [],
    description: str = "",
    rera_number: str = "",
    possession_date: str = "N/A",
    generation_type: str = "description",
    context: dict = {},
):
    try:
        if generation_type == "description":
            prompt = PROJECT_DESCRIPTION_PROMPT.format(
                project_name=project_name,
                builder=builder,
                city=city,
                status=status,
                property_type=property_type,
                starting_price=starting_price,
                max_price=max_price,
                configurations=", ".join(configurations) if configurations else "N/A",
                amenities=", ".join(amenities) if amenities else "N/A",
                highlights=", ".join(highlights) if highlights else "N/A",
                description=description or "N/A",
                rera_number=rera_number or "N/A",
                possession_date=possession_date,
            )
            result_text = await generate_text(prompt)
            return {
                "short_description": result_text[:200],
                "long_description": result_text,
                "seo_description": result_text[:160],
                "whatsapp_description": result_text[:300],
            }

        elif generation_type == "faqs":
            prompt = PROJECT_FAQ_PROMPT.format(
                project_name=project_name,
                builder=builder,
                city=city,
                property_type=property_type,
                configurations=", ".join(configurations) if configurations else "N/A",
                amenities=", ".join(amenities) if amenities else "N/A",
                rera_number=rera_number or "N/A",
                possession_date=possession_date,
            )
            result_text = await generate_text(prompt)
            try:
                import json
                if result_text.startswith("```json"):
                    result_text = result_text.replace("```json", "").replace("```", "").strip()
                faqs = json.loads(result_text)
                return {"faqs": faqs}
            except Exception:
                return {"faqs": [{"question": "Is this project RERA approved?", "answer": result_text}]}

        elif generation_type == "highlights":
            prompt = PROJECT_HIGHLIGHTS_PROMPT.format(
                project_name=project_name,
                builder=builder,
                city=city,
                property_type=property_type,
                starting_price=starting_price,
                configurations=", ".join(configurations) if configurations else "N/A",
                amenities=", ".join(amenities) if amenities else "N/A",
            )
            result_text = await generate_text(prompt)
            highlights_list = [line.strip("- ").strip() for line in result_text.split("\n") if line.strip()]
            return {"highlights": highlights_list}

        else:
            return {"message": f"Generation type '{generation_type}' not supported yet."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
