from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from llm.router import generate_json

router = APIRouter(
    prefix="/matching",
    tags=["Matching AI"]
)

class MatchUnitRequest(BaseModel):
    id: int
    name: str
    project: str
    price: float
    bedrooms: int
    bathrooms: int
    area_sqft: int
    address: str

class MatchRequest(BaseModel):
    lead_title: str
    lead_budget: Optional[float] = None
    lead_notes: str
    units: List[MatchUnitRequest]

class MatchItemResponse(BaseModel):
    id: int
    score: int
    reason: str

class MatchResponse(BaseModel):
    matches: List[MatchItemResponse]


@router.post("/match", response_model=MatchResponse)
async def match_lead_properties(request: MatchRequest):
    try:
        if not request.units:
            return MatchResponse(matches=[])

        units_list_str = []
        for u in request.units:
            units_list_str.append(
                f"- ID: {u.id}, Name: {u.name}, Project: {u.project}, Price: ${u.price}, Beds: {u.bedrooms}, Baths: {u.bathrooms}, Area: {u.area_sqft} sqft"
            )

        prompt = (
            f"You are a professional real estate matchmaking AI.\n"
            f"Compare the buyer lead requirements below with the available property listings and output a matching analysis.\n\n"
            f"Buyer Lead:\n"
            f"- Title: {request.lead_title}\n"
            f"- Budget: ${request.lead_budget if request.lead_budget else 'Not specified'}\n"
            f"- Notes/Preferences: {request.lead_notes}\n\n"
            f"Listings:\n"
            + "\n".join(units_list_str)
            + "\n\nFor each listing, calculate a percentage match score (0 to 100) and provide a concise, one-sentence rationale of how the price, size, and location match or mismatch the buyer's needs.\n"
            f"Return ONLY valid JSON matching this schema:\n"
            f"{{\n"
            f"  \"matches\": [\n"
            f"    {{\n"
            f"      \"id\": <unit_id>,\n"
            f"      \"score\": <int_score_0_to_100>,\n"
            f"      \"reason\": \"<concise_rationale_string>\"\n"
            f"    }}\n"
            f"  ]\n"
            f"}}"
        )

        res_data = await generate_json(prompt)
        
        # Ensure we return valid format even if model misbehaves
        matches_result = res_data.get("matches", [])
        validated_matches = []
        for m in matches_result:
            if "id" in m and "score" in m and "reason" in m:
                validated_matches.append(
                    MatchItemResponse(id=int(m["id"]), score=int(m["score"]), reason=str(m["reason"]))
                )
                
        return MatchResponse(matches=validated_matches)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI Matching Failed: {str(e)}"
        )
