from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.customers.views import (
    CustomerViewSet,
    CustomerAddressViewSet,
    CustomerRequirementViewSet,
    CustomerSourceViewSet,
    CustomerDocumentViewSet,
    CustomerNoteViewSet,
    CustomerActivityViewSet,
    CustomerCategoryViewSet,
    CustomerListViewSet,
)

router = DefaultRouter()
router.register(r"", CustomerViewSet, basename="customer")
router.register(r"addresses", CustomerAddressViewSet, basename="customer-address")
router.register(r"requirements", CustomerRequirementViewSet, basename="customer-requirement")
router.register(r"sources", CustomerSourceViewSet, basename="customer-source")
router.register(r"documents", CustomerDocumentViewSet, basename="customer-document")
router.register(r"notes", CustomerNoteViewSet, basename="customer-note")
router.register(r"activities", CustomerActivityViewSet, basename="customer-activity")
router.register(r"categories", CustomerCategoryViewSet, basename="customer-category")
router.register(r"lists", CustomerListViewSet, basename="customer-list")

urlpatterns = [
    path("", include(router.urls)),
]
