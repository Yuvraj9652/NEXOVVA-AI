from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    OrganizationViewSet,
    BranchViewSet,
    DepartmentViewSet,
    TeamViewSet,
)

router = DefaultRouter()
router.register("organizations", OrganizationViewSet)
router.register("branches", BranchViewSet)
router.register("departments", DepartmentViewSet)
router.register("teams", TeamViewSet)

urlpatterns = [
    path("", include(router.urls)),
]