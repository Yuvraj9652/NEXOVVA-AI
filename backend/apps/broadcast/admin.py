from django.contrib import admin
from apps.broadcast.models import (
    AudienceSegment,
    ContactList,
    BroadcastTemplate,
    Campaign,
    CampaignMessage,
    CampaignLog,
    CampaignAnalytics,
)


@admin.register(AudienceSegment)
class AudienceSegmentAdmin(admin.ModelAdmin):
    list_display = ["name", "segment_type", "customer_count", "created_at"]
    list_filter = ["segment_type", "created_at"]
    search_fields = ["name"]


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ["name", "contact_count", "created_at"]
    search_fields = ["name"]

    def contact_count(self, obj):
        return len(obj.contacts)


@admin.register(BroadcastTemplate)
class BroadcastTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "template_type", "language", "created_at"]
    list_filter = ["template_type", "language"]
    search_fields = ["name"]


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ["name", "campaign_type", "status", "total_reach", "created_at"]
    list_filter = ["status", "campaign_type", "created_at"]
    search_fields = ["name"]


@admin.register(CampaignMessage)
class CampaignMessageAdmin(admin.ModelAdmin):
    list_display = ["campaign", "customer_name", "channel", "status", "created_at"]
    list_filter = ["channel", "status", "created_at"]
    search_fields = ["customer_name", "customer_phone"]


@admin.register(CampaignLog)
class CampaignLogAdmin(admin.ModelAdmin):
    list_display = ["campaign", "action", "status", "created_at"]
    list_filter = ["action", "status", "created_at"]


@admin.register(CampaignAnalytics)
class CampaignAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["campaign", "updated_at"]