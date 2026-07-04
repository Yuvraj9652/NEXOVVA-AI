from rest_framework import viewsets, permissions
from apps.properties.serializers import ProjectSerializer, UnitSerializer
from apps.properties.selectors import PropertySelector
from apps.properties.services import PropertyService
from apps.authentication.permissions import IsOrganizationMember


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return PropertySelector.list_projects(organization=self.request.organization)

    def perform_create(self, serializer):
        project = PropertyService.create_project(
            organization=self.request.organization, **serializer.validated_data
        )
        serializer.instance = project


class UnitViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        bedrooms = self.request.query_params.get("bedrooms")
        bathrooms = self.request.query_params.get("bathrooms")

        # Parse numeric parameters safely
        min_p = float(min_price) if min_price else None
        max_p = float(max_price) if max_price else None
        beds = int(bedrooms) if bedrooms else None
        baths = int(bathrooms) if bathrooms else None

        return PropertySelector.search_units(
            organization=self.request.organization,
            min_price=min_p,
            max_price=max_p,
            bedrooms=beds,
            bathrooms=baths,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        project = validated_data.pop("project", None)
        project_id = project.id if project else None

        unit = PropertyService.create_unit(
            organization=self.request.organization, project_id=project_id, **validated_data
        )
        serializer.instance = unit
