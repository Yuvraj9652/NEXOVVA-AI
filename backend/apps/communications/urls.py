from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommunicationView, BroadcastCampaignViewSet

router = DefaultRouter()
router.register(r"campaigns", BroadcastCampaignViewSet, basename="campaign")

urlpatterns = [
    path("", CommunicationView.as_view(), name="communications"),
    path("", include(router.urls)),
]