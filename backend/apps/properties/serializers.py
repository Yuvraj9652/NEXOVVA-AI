from rest_framework import serializers
from apps.properties.models import Project, Unit, PropertyImage
from apps.knowledge_base.serializers import (
    ProjectMediaSerializer,
    ProjectDocumentSerializer,
    ProjectAmenitySerializer,
    ProjectTagSerializer,
    ProjectFAQSerializer,
    ProjectHighlightSerializer,
    ProjectAnalyticsSerializer,
    ProjectVersionSerializer,
)


class ProjectSerializer(serializers.ModelSerializer):
    media = ProjectMediaSerializer(many=True, read_only=True)
    documents = ProjectDocumentSerializer(many=True, read_only=True, source="kb_documents")
    amenities = ProjectAmenitySerializer(many=True, read_only=True)
    tags = ProjectTagSerializer(many=True, read_only=True, source="kb_tags")
    faqs = ProjectFAQSerializer(many=True, read_only=True)
    highlights = ProjectHighlightSerializer(many=True, read_only=True)
    analytics = ProjectAnalyticsSerializer(read_only=True, source="kb_analytics")
    versions = ProjectVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "short_description",
            "seo_description",
            "whatsapp_description",
            "status",
            "builder",
            "builder_logo",
            "image_url",
            "property_type",
            "configurations",
            "country",
            "state",
            "city",
            "area",
            "address",
            "google_map_url",
            "latitude",
            "longitude",
            "nearby_metro",
            "nearby_schools",
            "nearby_hospitals",
            "nearby_malls",
            "nearby_airport",
            "towers",
            "floors",
            "total_units",
            "sizes_sqft",
            "possession_date",
            "rera_number",
            "starting_price",
            "max_price",
            "price_per_sqft",
            "booking_amount",
            "payment_plan",
            "ai_processed",
            "ai_generated_keywords",
            "ai_generated_tags",
            "ai_generated_highlights",
            "ai_generated_investment_points",
            "ai_generated_summary",
            "rera_approved",
            "pet_friendly",
            "ready_possession",
            "metadata",
            "tags",
            "media",
            "documents",
            "amenities",
            "faqs",
            "highlights",
            "analytics",
            "versions",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


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
        read_only_fields = ["id", "images", "created_at", "updated_at"]
