from django.urls import path
from apps.reports.views import ReportsSummaryView

urlpatterns = [
    path("summary/", ReportsSummaryView.as_view(), name="reports_summary"),
]
