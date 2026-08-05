from rest_framework import serializers
from apps.broadcast.models import (
    AudienceSegment,
    ContactList,
    BroadcastTemplate,
    Campaign,
    CampaignMessage,
    CampaignLog,
    CampaignAnalytics,
)


class AudienceSegmentSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = AudienceSegment
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class ContactListSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ContactList
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class BroadcastTemplateSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = BroadcastTemplate
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class CampaignSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Campaign
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class CampaignMessageSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CampaignMessage
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at", "updated_at"]


class CampaignLogSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CampaignLog
        fields = "__all__"
        read_only_fields = ["id", "organization", "created_at"]


class CampaignAnalyticsSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = CampaignAnalytics
        fields = "__all__"
        read_only_fields = ["id", "organization", "updated_at"]


class CampaignSendSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    message = serializers.CharField()
    channel = serializers.ChoiceField(choices=["whatsapp", "email", "sms", "push", "sales_team", "crm"])


class CampaignScheduleSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    schedule_time = serializers.DateTimeField()
    recurring = serializers.BooleanField(default=False)
    timezone = serializers.CharField(default="UTC")


class CampaignImportSerializer(serializers.Serializer):
    file = serializers.FileField()
    list_name = serializers.CharField(required=False)


class CampaignPreviewSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    channel = serializers.ChoiceField(choices=["whatsapp", "email", "sms", "push"])


class AIAudienceMatchSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    query = serializers.CharField()
    filters = serializers.DictField(required=False, default={})


class AIContentGenerateSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    content_type = serializers.ChoiceField(
        choices=["whatsapp", "email", "sms", "push", "sales_script", "voice_script", "facebook", "instagram"]
    )
    audience_segment = serializers.CharField(required=False, default="")


class AIPersonalizeSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    customer_phone = serializers.CharField(required=False, default="")
    customer_email = serializers.EmailField(required=False, default="")
    content_type = serializers.ChoiceField(choices=["whatsapp", "email", "sms"])


class AIScheduleOptimizerSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    audience_size = serializers.IntegerField(required=False, default=100)


class AIDuplicateCheckSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    customer_phone = serializers.CharField()
    customer_email = serializers.EmailField(required=False, default="")


class AIFollowUpSerializer(serializers.Serializer):
    campaign_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    message_status = serializers.ChoiceField(choices=["opened", "replied", "clicked", "no_response"])
    days_since_sent = serializers.IntegerField(default=0)