import json

from google.genai.errors import APIError

from config.llm import (
    gemini_client,
    GEMINI_MODEL_NAME,
    groq_client,
    GROQ_MODEL_NAME,
)

from config.logger import logger


async def generate_text(prompt: str) -> str:

    # =========================
    # 1. Try Gemini
    # =========================
    try:
        logger.info("Sending text request to Gemini")

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
        )

        logger.info("Gemini response received successfully")

        return response.text

    except APIError as e:
        logger.warning(
            f"Gemini failed. Trying Groq fallback. Error: {e}"
        )

    except Exception as e:
        logger.warning(
            f"Unexpected Gemini error. Trying Groq fallback: {e}"
        )


    # =========================
    # 2. Fallback → Groq
    # =========================
    try:
        logger.info("Sending text request to Groq fallback")

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        logger.info("Groq fallback response received successfully")

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Groq fallback failed: {e}")

        raise Exception(
            f"Both Gemini and Groq failed. "
            f"Groq error: {e}"
        )


async def generate_json(prompt: str) -> dict:

    # =========================
    # 1. Try Gemini
    # =========================
    try:
        logger.info("Sending JSON request to Gemini")

        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt,
        )

        text = response.text.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        logger.warning(
            f"Gemini JSON generation failed. "
            f"Trying Groq fallback: {e}"
        )


    # =========================
    # 2. Fallback → Groq
    # =========================
    try:
        logger.info("Sending JSON request to Groq fallback")

        response = groq_client.chat.completions.create(
            model=GROQ_MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        text = response.choices[0].message.content.strip()

        if text.startswith("```json"):
            text = text.replace("```json", "").replace("```", "").strip()

        return json.loads(text)

    except Exception as e:
        logger.error(f"Groq JSON fallback failed: {e}")

        raise Exception(
            f"Both Gemini and Groq failed. "
            f"Groq error: {e}"
        )