from fastapi import FastAPI

from api.health import router as health_router
from config.settings import settings
from api.property_routes import router as property_router
from api.routes import router as chat_router
from api.email_routes import router as email_router
from api.lead_routes import router as lead_router
from api.summary_routes import router as summary_router
from api.recommendation_routes import router as recommendation_router
from api.conversation_routes import router as conversation_router
from api.rag_routes import router as rag_router
from api.document_chat_routes import router as document_chat_router
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(property_router)
app.include_router(email_router)
app.include_router(lead_router)
app.include_router(summary_router)
app.include_router(recommendation_router)
app.include_router(conversation_router)
app.include_router(rag_router)
app.include_router(document_chat_router)
@app.get("/")
async def root():
    return {
        "message": "Welcome to NEXOVVA AI Service"
    }