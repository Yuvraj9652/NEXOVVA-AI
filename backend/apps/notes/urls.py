from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.notes.views import NoteViewSet

router = DefaultRouter()
router.register(r"", NoteViewSet, basename="note")

urlpatterns = [
    path("", include(router.urls)),
]
