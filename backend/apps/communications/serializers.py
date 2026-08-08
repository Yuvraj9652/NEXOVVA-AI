from rest_framework import serializers
from .models import BroadcastCampaign


class BroadcastCampaignSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BroadcastCampaign
        fields = [
            "id", "organization", "name", "subject", "status", "target_type",
            "project", "project_name", "selected_customer_ids", "reach",
            "total_sent", "open_rate", "click_rate", "conversion_rate",
            "image_url", "content", "date", "scheduled_at", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "organization", "created_at", "updated_at"]
