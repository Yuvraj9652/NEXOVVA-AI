from google import genai

from config.settings import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = settings.MODEL_NAME