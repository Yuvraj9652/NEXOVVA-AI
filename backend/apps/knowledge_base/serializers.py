from rest_framework import serializers
from apps.knowledge_base.models import (
    ProjectCategory,
    ProjectMedia,
    ProjectDocument,
    ProjectAmenity,
    ProjectVersion,
    ProjectAnalytics,
    ProjectTag,
    ProjectFAQ,
    ProjectHighlight,
    ProjectProcessingJob,
    ProjectChatSession,
    ProjectChatMessage,
)


class ProjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ["id", "name", "description", "color", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectMedia
        fields = [
            "id", "project", "media_type", "file", "thumbnail",
            "caption", "is_primary", "sort_order", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        fields = [
            "id", "project", "document_type", "name", "file", "file_size",
            "version", "processed", "extracted_data", "created_at", "updated_at"
        ]
        read_only_fields = [
            "id", "version", "processed", "extracted_data", "file_size", "created_at", "updated_at"
        ]


class ProjectAmenitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAmenity
        fields = [
            "id", "project", "amenity_type", "custom_name", "description",
            "icon", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectVersionSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = ProjectVersion
        fields = [
            "id", "project", "version_number", "change_summary", "changed_fields",
            "snapshot", "created_by", "created_by_name", "created_at"
        ]
        read_only_fields = ["id", "created_at"]


class ProjectAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectAnalytics
        fields = [
            "id", "project", "interested_customers", "ai_recommendations",
            "brochure_downloads", "video_views", "site_visits", "bookings",
            "revenue", "conversion_rate", "updated_at"
        ]
        read_only_fields = ["id", "updated_at"]


class ProjectTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ["id", "project", "name", "color", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectFAQ
        fields = [
            "id", "project", "question", "answer", "is_ai_generated",
            "sort_order", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectHighlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectHighlight
        fields = ["id", "project", "text", "icon", "sort_order", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectProcessingJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectProcessingJob
        fields = [
            "id", "project", "job_type", "status", "progress",
            "result", "error_message", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProjectChatSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectChatSession
        fields = ["id", "project", "session_id", "title", "created_by", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "session_id", "created_at", "updated_at"]


class ProjectChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectChatMessage
        fields = ["id", "session", "role", "content", "metadata", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProjectBulkImportPreviewSerializer(serializers.Serializer):
    projects = serializers.ListField(child=serializers.DictField())
    total = serializers.IntegerField()
    valid = serializers.IntegerField()
    invalid = serializers.IntegerField()
