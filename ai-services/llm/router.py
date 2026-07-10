import json

from google.genai.errors import APIError

from config.llm import client, MODEL_NAME
from config.logger import logger


async def generate_text(prompt: str) -> str:
    try:
        logger.info("Sending text request to Gemini")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        return response.text

    except APIError as e:
        logger.error(f"Gemini API Error: {e}")
        raise Exception(f"Gemini API Error: {e}")

    except Exception as e:
        logger.error(str(e))
        raise Exception(str(e))


async def generate_json(prompt: str) -> dict:
    try:
        logger.info("Sending JSON request to Gemini")

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        logger.error(str(e))
        raise Exception(str(e))
