from pydantic import BaseModel
from typing import Optional, Dict, Any, List


class ProjectChatRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[Dict[str, Any]] = {}


class ProjectChatResponse(BaseModel):
    response: str


class ProjectAIGenerateRequest(BaseModel):
    project_name: str
    builder: str
    city: str
    status: str
    property_type: str
    starting_price: str
    max_price: str
    configurations: List[str] = []
    amenities: List[str] = []
    highlights: List[str] = []
    description: str = ""
    rera_number: str = ""
    possession_date: str = "N/A"
    generation_type: str = "description"
    context: Optional[Dict[str, Any]] = {}


class ProjectAIGenerateResponse(BaseModel):
    result: Dict[str, Any]
