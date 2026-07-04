from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.properties.views import ProjectViewSet, UnitViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="project")
router.register(r"units", UnitViewSet, basename="unit")

urlpatterns = [
    path("", include(router.urls)),
]
