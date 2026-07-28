import logging
import time
import requests
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
    def call_chat(cls, session_id: str, message: str) -> str:
        """
        Sends the user message to the FastAPI AI Service /chat/ endpoint.
        Implements timeouts, retries, error handling, and latency logging.
        """
        url = urljoin(settings.AI_SERVICE_URL, "/chat/")
        timeout = getattr(settings, "AI_SERVICE_TIMEOUT", 30.0)

        payload = {
            "session_id": str(session_id),
            "message": message
        }

        max_retries = 3
        backoff = 0.5

        start_time = time.time()
        logger.info(f"User message sent to AI Service - Session: {session_id} - Content: {message[:100]}")

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=timeout
                )
                latency = time.time() - start_time
                logger.info(f"AI Service response received in {latency:.4f}s - Attempt {attempt + 1}")

                if response.status_code == 200:
                    try:
                        res_data = response.json()
                        reply = res_data.get("response", "")
                        logger.info(f"AI response successfully parsed: {reply[:100]}...")
                        return reply
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
