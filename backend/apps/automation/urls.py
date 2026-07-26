from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.automation.views import AutomationRuleViewSet, WorkflowRunView

router = DefaultRouter()
router.register(r"rules", AutomationRuleViewSet, basename="rule")

urlpatterns = [
    path("run-workflow/", WorkflowRunView.as_view(), name="run_workflow"),
    path("", include(router.urls)),
]
