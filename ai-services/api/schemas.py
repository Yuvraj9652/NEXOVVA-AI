from pydantic import BaseModel
from typing import List

class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str



class PropertyDescriptionRequest(BaseModel):
    property_type: str
    city: str
    bedrooms: int
    bathrooms: int
    price: str
    features: List[str]


class PropertyDescriptionResponse(BaseModel):
    description: str

class EmailRequest(BaseModel):
    customer_name: str
    property_name: str
    property_type: str
    city: str
    budget: str


class EmailResponse(BaseModel):
    email: str

class LeadScoreRequest(BaseModel):
    customer_name: str
    budget: str
    timeline: str
    interest_level: str
    property_type: str


class LeadScoreResponse(BaseModel):
    score: int
    category: str
    reason: str



class MeetingSummaryRequest(BaseModel):
    transcript: str


class MeetingSummaryResponse(BaseModel):
    summary: str
    key_points: List[str]
    action_items: List[str]


class RecommendationRequest(BaseModel):
    budget: str
    city: str
    family_size: int
    property_type: str
    preferences: List[str]


class RecommendationResponse(BaseModel):
    recommended_property: str
    reason: str
    important_features: List[str]

class ChatRequest(BaseModel):
    session_id: str
    message: str


class AskDocumentRequest(BaseModel):
    filename: str
    question: str


class AskDocumentResponse(BaseModel):
    answer: str
    sources: list