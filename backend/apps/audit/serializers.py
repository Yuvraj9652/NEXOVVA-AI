from rest_framework import serializers
from apps.audit.models import ActivityLog
from apps.authentication.serializers import UserSerializer


class ActivityLogSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source="user", read_only=True)

    class Meta:
        model = ActivityLog
        fields = [
            "id",
            "user_details",
            "action",
            "target_type",
            "target_id",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "user_details", "created_at"]
