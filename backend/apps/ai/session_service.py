import logging
import uuid
from apps.ai.models import AIChatSession
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

logger = logging.getLogger("ai_service")


class SessionService:
    @classmethod
    def create_session(cls, user, organization, title="New Conversation") -> AIChatSession:
        """
        Creates a new AI chat session for a user and organization (tenant).
        """
        session = AIChatSession.objects.create(
            user=user,
            organization=organization,
            title=title,
            status="ACTIVE"
        )
        logger.info(f"AI Chat Session created - ID: {session.id} - User: {user.username} - Organization: {organization.id}")
        return session

    @classmethod
    def archive_session(cls, session_id: str, user, organization) -> AIChatSession:
        """
        Archives an existing AI chat session by changing status to ARCHIVED.
        """
        try:
            uuid.UUID(str(session_id))
        except ValueError:
            raise ValidationError("Invalid session UUID format.")

        session = AIChatSession.objects.get(id=session_id, user=user, organization=organization)
        session.status = "ARCHIVED"
        session.save()
        logger.info(f"AI Chat Session archived - ID: {session.id}")
        return session

    @classmethod
    def retrieve_session(cls, session_id: str, user, organization) -> AIChatSession:
        """
        Retrieves a session ensuring tenant isolation and ownership.
        """
        try:
            uuid.UUID(str(session_id))
        except ValueError:
            raise ValidationError("Invalid session UUID format.")

        return AIChatSession.objects.get(id=session_id, user=user, organization=organization)

    @classmethod
    def get_or_create_session(cls, session_id: str, user, organization) -> AIChatSession:
        """
        Gets a session by ID or initializes a new one under the user and organization context.
        """
        try:
            uuid_val = uuid.UUID(str(session_id))
        except ValueError:
            raise ValidationError("Invalid session UUID format.")

        session, created = AIChatSession.objects.get_or_create(
            id=uuid_val,
            defaults={
                "user": user,
                "organization": organization,
                "title": "Auto-initialized Chat",
                "status": "ACTIVE"
            }
        )
        if created:
            logger.info(f"AI Chat Session auto-initialized - ID: {session.id} - User: {user.username}")
        return session
