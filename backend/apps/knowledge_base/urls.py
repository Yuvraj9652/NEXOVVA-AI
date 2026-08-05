from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.knowledge_base.views import (
    ProjectCategoryViewSet,
    ProjectViewSet,
    ProjectMediaViewSet,
    ProjectDocumentViewSet,
    ProjectAmenityViewSet,
    ProjectVersionViewSet,
    ProjectAnalyticsView,
    ProjectTagViewSet,
    ProjectFAQViewSet,
    ProjectHighlightViewSet,
    ProjectProcessingJobViewSet,
    ProjectChatSessionViewSet,
    ProjectExportView,
    ProjectAIGenerateView,
)

router = DefaultRouter()
router.register(r"categories", ProjectCategoryViewSet, basename="project-category")
router.register(r"", ProjectViewSet, basename="project")
router.register(r"media", ProjectMediaViewSet, basename="project-media")
router.register(r"documents", ProjectDocumentViewSet, basename="project-document")
router.register(r"amenities", ProjectAmenityViewSet, basename="project-amenity")
router.register(r"versions", ProjectVersionViewSet, basename="project-version")
router.register(r"jobs", ProjectProcessingJobViewSet, basename="project-job")
router.register(r"chat-sessions", ProjectChatSessionViewSet, basename="project-chat-session")
router.register(r"tags", ProjectTagViewSet, basename="project-tag")
router.register(r"faqs", ProjectFAQViewSet, basename="project-faq")
router.register(r"highlights", ProjectHighlightViewSet, basename="project-highlight")

urlpatterns = [
    path("", include(router.urls)),
    path("analytics/", ProjectAnalyticsView.as_view(), name="project-analytics"),
    path("export/", ProjectExportView.as_view(), name="project-export"),
    path("ai-generate/<int:project_id>/", ProjectAIGenerateView.as_view(), name="project-ai-generate"),
]
