from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.authentication.urls")),
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
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
