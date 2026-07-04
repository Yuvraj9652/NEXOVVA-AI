from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.pipeline.views import PipelineStageViewSet, DealViewSet

router = DefaultRouter()
router.register(r"stages", PipelineStageViewSet, basename="stage")
router.register(r"deals", DealViewSet, basename="deal")

urlpatterns = [
    path("", include(router.urls)),
]
