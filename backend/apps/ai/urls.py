from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ai.views import PromptTemplateViewSet, ChatSessionViewSet, AIAnalyticsView, RAGAskView, AIMatchingView, AICommandCenterView
from apps.ai.webhook_views import InboundWebhookView

router = DefaultRouter()
router.register(r"templates", PromptTemplateViewSet, basename="template")
router.register(r"sessions", ChatSessionViewSet, basename="session")

urlpatterns = [
    path("analytics/", AIAnalyticsView.as_view(), name="ai_analytics"),
    path("ask-document/", RAGAskView.as_view(), name="rag_ask"),
    path("matching/", AIMatchingView.as_view(), name="ai_matching"),
    path("inbound-webhook/", InboundWebhookView.as_view(), name="ai_inbound_webhook"),
    path("command-center/", AICommandCenterView.as_view(), name="ai_command_center"),
    path("", include(router.urls)),
]
