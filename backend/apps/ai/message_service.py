import logging
from apps.ai.models import AIChatMessage, AIChatSession

logger = logging.getLogger("ai_service")


class MessageService:
    @classmethod
    def save_user_message(cls, session: AIChatSession, content: str) -> AIChatMessage:
        """
        Saves a user message to the database.
        """
        msg = AIChatMessage.objects.create(
            session=session,
            role=AIChatMessage.Roles.USER,
            content=content
        )
        logger.info(f"User message saved in DB - Session: {session.id} - Msg ID: {msg.id}")
        return msg

    @classmethod
    def save_ai_message(cls, session: AIChatSession, content: str) -> AIChatMessage:
        """
        Saves an AI/assistant message to the database.
        """
        msg = AIChatMessage.objects.create(
            session=session,
            role=AIChatMessage.Roles.ASSISTANT,
            content=content
        )
        logger.info(f"AI message saved in DB - Session: {session.id} - Msg ID: {msg.id}")
        return msg

    @classmethod
    def retrieve_history(cls, session: AIChatSession):
        """
        Retrieves the chronological list of messages in a session.
        """
        return AIChatMessage.objects.filter(session=session).order_by("created_at")
