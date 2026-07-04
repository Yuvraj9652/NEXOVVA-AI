from rest_framework import serializers
from apps.properties.models import Project, Unit, PropertyImage


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "name", "description", "latitude", "longitude", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "image", "is_primary"]


class UnitSerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    project_details = ProjectSerializer(source="project", read_only=True)
    project = serializers.PrimaryKeyRelatedField(
        queryset=Project.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Unit
        fields = [
            "id",
            "project",
            "project_details",
            "name",
            "address",
            "price",
            "bedrooms",
            "bathrooms",
            "area_sqft",
            "status",
            "latitude",
            "longitude",
            "images",
            "created_at",
        ]
        read_only_fields = ["id", "images", "created_at"]
