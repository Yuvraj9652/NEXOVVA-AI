from rest_framework import serializers
from apps.ai.models import PromptTemplate, AIChatSession, AIChatMessage, AIUsage


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = ["id", "name", "template", "purpose"]


class AIChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatSession
        fields = ["id", "title", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "created_at", "updated_at"]


class AIChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIChatMessage
        fields = ["role", "content", "created_at"]
        read_only_fields = ["created_at"]


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(required=True)


class ChatResponseSerializer(serializers.Serializer):
    content = serializers.CharField(required=True)


class AIUsageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = AIUsage
        fields = [
            "id",
            "username",
            "model_name",
            "prompt_tokens",
            "completion_tokens",
            "cost",
            "created_at",
        ]
        read_only_fields = ["id", "username", "created_at"]


# Aliases to match requirements exactly
AIChatSession = AIChatSessionSerializer
AIChatMessage = AIChatMessageSerializer
ChatRequest = ChatRequestSerializer
ChatResponse = ChatResponseSerializer

