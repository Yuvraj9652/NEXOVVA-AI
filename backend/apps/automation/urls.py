from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.automation.views import AutomationRuleViewSet

router = DefaultRouter()
router.register(r"rules", AutomationRuleViewSet, basename="rule")

urlpatterns = [
    path("", include(router.urls)),
]
