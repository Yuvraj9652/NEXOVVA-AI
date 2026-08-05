import logging
import time
import requests
import json
from django.conf import settings
from urllib.parse import urljoin

logger = logging.getLogger("ai_service")


class AIServiceException(Exception):
    """Base exception for AI Service integration issues."""
    pass


class AIServiceOfflineException(AIServiceException):
    """Exception raised when the AI Service is unreachable."""
    pass


class AIServiceTimeoutException(AIServiceException):
    """Exception raised when the AI Service requests time out."""
    pass


class AIService:
    @classmethod
    def _post(cls, path: str, payload: dict) -> dict:
        """Helper to send a POST request to the FastAPI AI service."""
        url = urljoin(settings.AI_SERVICE_URL, path)
        timeout = getattr(settings, "AI_SERVICE_TIMEOUT", 30.0)
        
        max_retries = 3
        backoff = 0.5
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout
                )
                if response.status_code == 200:
                    try:
                        return response.json()
                    except ValueError as e:
                        logger.error(f"Failed to parse JSON response from AI service: {e}")
                        raise AIServiceException("Invalid JSON response from AI service")
                else:
                    logger.error(f"AI service error {response.status_code}: {response.text}")
                    raise AIServiceException(f"AI service returned status code {response.status_code}")

            except requests.exceptions.Timeout as e:
                logger.warning(f"Timeout on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise AIServiceTimeoutException("AI service request timed out.")
                time.sleep(backoff * (2 ** attempt))

            except requests.exceptions.ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise AIServiceOfflineException("AI service is offline.")
                time.sleep(backoff * (2 ** attempt))

            except Exception as e:
                logger.error(f"Unexpected error calling AI service: {e}")
                raise AIServiceException(f"Unexpected error calling AI service: {str(e)}")
        
        raise AIServiceException("AI service call failed after retries.")

    @classmethod
    def chat(cls, session_id: str, message: str) -> str:
        """Sends a user message to the /chat/ endpoint and returns the text response."""
        payload = {
            "session_id": str(session_id),
            "message": message
        }
        res = cls._post("/chat/", payload)
        return res.get("response", "")

    @classmethod
    def ask_rag(cls, filename: str, question: str, organization_id: str) -> str:
        """Sends a RAG query for a document to the /documents/ask endpoint."""
        payload = {
            "filename": filename,
            "question": question,
            "organization_id": str(organization_id)
        }
        res = cls._post("/documents/ask", payload)
        return res.get("answer", "")

    @classmethod
    def call_project_chat(cls, session_id: str, message: str, context: dict) -> str:
        """Sends a context-aware chat message to /project-chat/."""
        payload = {
            "session_id": str(session_id),
            "message": message,
            "context": context
        }
        res = cls._post("/project-chat/", payload)
        return res.get("response", "No response from AI.")

    @classmethod
    def call_project_ai_generate(cls, payload: dict) -> dict:
        """Sends a generation task payload to /project-ai-generate/."""
        return cls._post("/project-ai-generate/", payload)

    @classmethod
    def generate_structured_output(cls, prompt_text: str, schema: dict) -> dict:
        """
        Sends a request to /chat/ instructing the LLM to output structured JSON
        matching the provided schema dictionary.
        """
        system_instruction = (
            f"You must return response in structured JSON format matching this schema: {schema}. "
            "Return only the JSON string inside a JSON block."
        )
        payload = {
            "session_id": "structured_gen",
            "message": f"{system_instruction}\n\nInput: {prompt_text}"
        }
        res_data = cls._post("/chat/", payload)
        response_text = res_data.get("response", "")
        
        # Clean up any potential markdown wrap
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except Exception as e:
            try:
                return json.loads(response_text)
            except Exception:
                logger.error(f"Failed to parse structured JSON: {response_text}. Error: {e}")
                return {"reply": response_text, "error": "Failed to parse structured response"}

    @classmethod
    def summarize(cls, text: str) -> str:
        """Calls /chat/ with a summarization task prompt."""
        payload = {
            "session_id": "summarize_run",
            "message": f"Generate a brief summary of the following customer interaction logs:\n\n{text}"
        }
        res = cls._post("/chat/", payload)
        return res.get("response", "")
