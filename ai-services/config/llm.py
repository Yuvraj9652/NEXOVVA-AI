from google import genai
from groq import Groq

from config.settings import settings

# Gemini - Primary

gemini_client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)

GEMINI_MODEL_NAME = settings.MODEL_NAME

client = gemini_client
MODEL_NAME = GEMINI_MODEL_NAME

# Groq - Fallback

groq_client = Groq(
    api_key=settings.GROQ_API_KEY
)

GROQ_MODEL_NAME = settings.GROQ_MODEL