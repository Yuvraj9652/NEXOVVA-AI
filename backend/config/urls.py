from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/contacts/", include("apps.contacts.urls")),
    path("api/leads/", include("apps.leads.urls")),
    path("api/pipeline/", include("apps.pipeline.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
    path("api/notes/", include("apps.notes.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("api/ai/", include("apps.ai.urls")),
    path("api/customers/", include("apps.customers.urls")),
    path("api/properties/", include("apps.properties.urls")),
    path("api/documents/", include("apps.documents.urls")),
    path("api/notifications/", include("apps.notifications.urls")),
    path("api/automation/", include("apps.automation.urls")),
    path("api/reports/", include("apps.reports.urls")),
    path("api/dashboard/", include("apps.dashboard.urls")),
    path("api/analytics/", include("apps.analytics.urls")),
    path("api/communications/", include("apps.communications.urls")),
    path("api/calendar/", include("apps.calendar.urls")),
    path("api/billing/", include("apps.billing.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/organizations/", include("apps.organizations.urls")),
    path("api/employees/", include("apps.employees.urls")),
    path("api/companies/", include("apps.companies.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
