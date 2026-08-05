from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from llm.router import generate_text, generate_json
from config.prompts import (
    PROJECT_DESCRIPTION_PROMPT,
    PROJECT_FAQ_PROMPT,
    PROJECT_HIGHLIGHTS_PROMPT,
    PROJECT_CHAT_SYSTEM_PROMPT,
)
from config.logger import logger

router = APIRouter()

GENERATION_TYPE_ALIASES = {
    "description": "description",
    "description_generation": "description",
    "descriptions": "description",
    "faqs": "faqs",
    "faq": "faqs",
    "highlights": "highlights",
    "highlight": "highlights",
    "keywords": "keywords",
    "tags": "tags",
    "summary": "summary",
    "investment_points": "investment_points",
}


class AIGenerateRequest(BaseModel):
    generation_type: str = "description"
    project_name: str = "N/A"
    builder: str = "N/A"
    city: str = "N/A"
    status: str = "N/A"
    property_type: str = "N/A"
    starting_price: str = "N/A"
    max_price: str = "N/A"
    configurations: list = []
    amenities: list = []
    highlights: list = []
    description: str = ""
    rera_number: str = "N/A"
    possession_date: str = "N/A"
    context: dict = {}

    model_config = {"extra": "allow"}

    def _fmt(self, key: str) -> str:
        value = getattr(self, key, "N/A")
        if key in ("configurations", "amenities", "highlights") and isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value) or "N/A"
        if value in (None, ""):
            return "N/A"
        return str(value)


@router.post("/project-ai-generate/")
async def project_ai_generate(request: AIGenerateRequest):
    gen_type = GENERATION_TYPE_ALIASES.get(
        request.generation_type, request.generation_type
    )
    logger.info(f"AI generate request - type: {request.generation_type} -> {gen_type}")

    try:
        if gen_type == "description":
            prompt = PROJECT_DESCRIPTION_PROMPT.format(
                project_name=request._fmt("project_name"),
                builder=request._fmt("builder"),
                city=request._fmt("city"),
                status=request._fmt("status"),
                property_type=request._fmt("property_type"),
                starting_price=request._fmt("starting_price"),
                max_price=request._fmt("max_price"),
                configurations=request._fmt("configurations"),
                amenities=request._fmt("amenities"),
                highlights=request._fmt("highlights"),
                rera_number=request._fmt("rera_number"),
                possession_date=request._fmt("possession_date"),
                description=request._fmt("description"),
            )
            return await generate_json(prompt)

        if gen_type == "faqs":
            prompt = PROJECT_FAQ_PROMPT.format(
                project_name=request._fmt("project_name"),
                builder=request._fmt("builder"),
                city=request._fmt("city"),
                property_type=request._fmt("property_type"),
                configurations=request._fmt("configurations"),
                amenities=request._fmt("amenities"),
                rera_number=request._fmt("rera_number"),
                possession_date=request._fmt("possession_date"),
            )
            return await generate_json(prompt)

        if gen_type == "highlights":
            prompt = PROJECT_HIGHLIGHTS_PROMPT.format(
                project_name=request._fmt("project_name"),
                builder=request._fmt("builder"),
                city=request._fmt("city"),
                property_type=request._fmt("property_type"),
                starting_price=request._fmt("starting_price"),
                max_price=request._fmt("max_price"),
                configurations=request._fmt("configurations"),
                amenities=request._fmt("amenities"),
            )
            text = await generate_text(prompt)
            highlights = [
                line.strip().lstrip("- ").strip()
                for line in text.splitlines()
                if line.strip()
            ]
            return {"highlights": highlights}

        prompt = (
            f"{PROJECT_CHAT_SYSTEM_PROMPT.format(**request.__dict__)}\n\n"
            f"Task: {request.generation_type}\n"
            f"Project Name: {request._fmt('project_name')}\n"
            f"Description: {request._fmt('description')}\n"
        )
        text = await generate_text(prompt)
        return {"generation_type": request.generation_type, "content": text}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generate failed: {e}")
        raise HTTPException(status_code=502, detail=f"AI generation failed: {str(e)}")
