from rest_framework import serializers
from apps.ai.models import PromptTemplate, ChatSession, ChatMessage, AIUsage


class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = ["id", "name", "template", "purpose"]


class ChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ["id", "title", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "role", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatMessageRequestSerializer(serializers.Serializer):
    message = serializers.CharField()


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
