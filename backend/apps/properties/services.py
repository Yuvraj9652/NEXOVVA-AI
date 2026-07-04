from django.db import transaction
from apps.properties.models import Project, Unit, PropertyImage


class PropertyService:
    @staticmethod
    @transaction.atomic
    def create_project(
        organization, name, description="", latitude=None, longitude=None, metadata=None
    ):
        return Project.objects.create(
            organization=organization,
            name=name,
            description=description,
            latitude=latitude,
            longitude=longitude,
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def create_unit(
        organization,
        name,
        price,
        bedrooms=0,
        bathrooms=0,
        area_sqft=0,
        address="",
        status=Unit.Statuses.AVAILABLE,
        latitude=None,
        longitude=None,
        project_id=None,
    ):
        project = (
            Project.objects.get(organization=organization, id=project_id) if project_id else None
        )
        return Unit.objects.create(
            organization=organization,
            name=name,
            price=price,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            area_sqft=area_sqft,
            address=address,
            status=status,
            latitude=latitude,
            longitude=longitude,
            project=project,
        )
