from django.db import models
from apps.properties.models import Project, Unit


class PropertySelector:
    @staticmethod
    def list_projects(organization):
        return Project.objects.filter(organization=organization)

    @staticmethod
    def search_units(
        organization,
        min_price=None,
        max_price=None,
        bedrooms=None,
        bathrooms=None,
        min_lat=None,
        max_lat=None,
        min_lng=None,
        max_lng=None,
    ):
        queryset = (
            Unit.objects.filter(organization=organization)
            .select_related("project")
            .prefetch_related("images")
        )

        if min_price is not None:
            queryset = queryset.filter(price__gte=min_price)
        if max_price is not None:
            queryset = queryset.filter(price__lte=max_price)
        if bedrooms is not None:
            queryset = queryset.filter(bedrooms=bedrooms)
        if bathrooms is not None:
            queryset = queryset.filter(bathrooms=bathrooms)

        # Geographic boundary search
        if min_lat is not None and max_lat is not None:
            queryset = queryset.filter(latitude__range=(min_lat, max_lat))
        if min_lng is not None and max_lng is not None:
            queryset = queryset.filter(longitude__range=(min_lng, max_lng))

        return queryset
