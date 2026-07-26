from rest_framework import serializers
from .models import BroadcastCampaign


class BroadcastCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = BroadcastCampaign
        fields = ["id", "name", "status", "reach", "date", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
