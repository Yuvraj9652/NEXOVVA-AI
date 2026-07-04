from django.db import models
from apps.ai.models import ChatSession, ChatMessage, AIUsage, PromptTemplate


class AISelector:
    @staticmethod
    def list_sessions(organization, user):
        return ChatSession.objects.filter(organization=organization, user=user)

    @staticmethod
    def get_session(organization, session_id):
        return ChatSession.objects.get(organization=organization, id=session_id)

    @staticmethod
    def list_messages(session):
        return ChatMessage.objects.filter(session=session).order_by("created_at")

    @staticmethod
    def list_templates():
        return PromptTemplate.objects.all()

    @staticmethod
    def get_usage_analytics(organization):
        # Return aggregated metrics
        usages = AIUsage.objects.filter(organization=organization)
        aggregates = usages.aggregate(
            total_prompt_tokens=models.Sum("prompt_tokens"),
            total_completion_tokens=models.Sum("completion_tokens"),
            total_cost=models.Sum("cost"),
            total_requests=models.Count("id"),
        )
        return {
            "total_prompt_tokens": aggregates["total_prompt_tokens"] or 0,
            "total_completion_tokens": aggregates["total_completion_tokens"] or 0,
            "total_cost": float(aggregates["total_cost"] or 0.0),
            "total_requests": aggregates["total_requests"] or 0,
        }
