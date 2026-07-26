from django.urls import path
from .views import DashboardView, ProjectAnalyticsView

urlpatterns = [
    path("", DashboardView.as_view()),
    path("analytics/", ProjectAnalyticsView.as_view(), name="project_analytics"),
]