from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.ai.views import PromptTemplateViewSet, ChatSessionViewSet, AIAnalyticsView

router = DefaultRouter()
router.register(r"templates", PromptTemplateViewSet, basename="template")
router.register(r"sessions", ChatSessionViewSet, basename="session")

urlpatterns = [
    path("analytics/", AIAnalyticsView.as_view(), name="ai_analytics"),
    path("", include(router.urls)),
]
