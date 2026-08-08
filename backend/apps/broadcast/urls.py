from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.broadcast.views import (
    AudienceSegmentViewSet,
    ContactListViewSet,
    BroadcastTemplateViewSet,
    CampaignViewSet,
    CampaignMessageViewSet,
    CampaignLogViewSet,
    CampaignAnalyticsView,
    AIAudienceMatchView,
    AIContentGenerateView,
    AIPersonalizeView,
    AIScheduleOptimizerView,
    AIDuplicateCheckView,
    AIFollowUpView,
)

router = DefaultRouter()
router.register(r"audience-segments", AudienceSegmentViewSet, basename="audience-segment")
router.register(r"contact-lists", ContactListViewSet, basename="contact-list")
router.register(r"templates", BroadcastTemplateViewSet, basename="broadcast-template")
router.register(r"campaigns", CampaignViewSet, basename="campaign")
router.register(r"messages", CampaignMessageViewSet, basename="campaign-message")
router.register(r"logs", CampaignLogViewSet, basename="campaign-log")

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", CampaignAnalyticsView.as_view(), name="campaign-analytics"),
    path("ai/audience-match/", AIAudienceMatchView.as_view(), name="ai-audience-match"),
    path("ai/generate-content/", AIContentGenerateView.as_view(), name="ai-generate-content"),
    path("ai/personalize/", AIPersonalizeView.as_view(), name="ai-personalize"),
    path("ai/optimize-schedule/", AIScheduleOptimizerView.as_view(), name="ai-optimize-schedule"),
    path("ai/check-duplicate/", AIDuplicateCheckView.as_view(), name="ai-check-duplicate"),
    path("ai/follow-up/", AIFollowUpView.as_view(), name="ai-follow-up"),
]