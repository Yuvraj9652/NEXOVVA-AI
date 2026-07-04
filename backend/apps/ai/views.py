from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.ai.models import PromptTemplate, ChatSession, ChatMessage
from apps.ai.serializers import (
    PromptTemplateSerializer,
    ChatSessionSerializer,
    ChatMessageSerializer,
    ChatMessageRequestSerializer,
)
from apps.ai.selectors import AISelector
from apps.ai.services import GeminiService
from apps.authentication.permissions import IsOrganizationMember


class PromptTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = PromptTemplateSerializer
    queryset = PromptTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return AISelector.list_sessions(
            organization=self.request.organization, user=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, user=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        session = self.get_object()
        msgs = AISelector.list_messages(session=session)
        serializer = ChatMessageSerializer(msgs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        session = self.get_object()
        req_serializer = ChatMessageRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        user_message = req_serializer.validated_data["message"]

        ai_response = GeminiService.generate_chat_response(
            organization=request.organization,
            user=request.user,
            session_id=session.id,
            user_message_text=user_message,
        )

        last_msg = ChatMessage.objects.filter(session=session).last()
        serializer = ChatMessageSerializer(last_msg)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AIAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        analytics = AISelector.get_usage_analytics(organization=request.organization)
        return Response(analytics)
