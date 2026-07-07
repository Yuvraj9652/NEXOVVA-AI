from django.urls import path

from .views import CommunicationView

urlpatterns = [
    path("", CommunicationView.as_view(), name="communications"),
]