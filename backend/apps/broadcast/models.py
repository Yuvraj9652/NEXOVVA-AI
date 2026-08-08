import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TenantModel


class AudienceSegment(TenantModel):
    class SegmentType(models.TextChoices):
        MANUAL = "MANUAL", "Manual"
        AUTOMATED = "AUTOMATED", "Automated"
        AI_MATCHED = "AI_MATCHED", "AI Matched"
        CSV_IMPORT = "CSV_IMPORT", "CSV Import"

    name = models.CharField(max_length=255)
    segment_type = models.CharField(max_length=20, choices=SegmentType.choices, default=SegmentType.MANUAL)
    filters = models.JSONField(default=dict, blank=True)
    customer_count = models.IntegerField(default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_segments"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.customer_count} contacts)"


class ContactList(TenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    contacts = models.JSONField(default=list, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_contact_lists"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class BroadcastTemplate(TenantModel):
    class TemplateType(models.TextChoices):
        WHATSAPP = "WHATSAPP", "WhatsApp"
        EMAIL = "EMAIL", "Email"
        SMS = "SMS", "SMS"
        PUSH_NOTIFICATION = "PUSH_NOTIFICATION", "Push Notification"
        SALES_SCRIPT = "SALES_SCRIPT", "Sales Script"
        VOICE_SCRIPT = "VOICE_SCRIPT", "Voice Call Script"
        FACEBOOK_POST = "FACEBOOK_POST", "Facebook Post"
        INSTAGRAM_CAPTION = "INSTAGRAM_CAPTION", "Instagram Caption"

    name = models.CharField(max_length=255)
    template_type = models.CharField(max_length=30, choices=TemplateType.choices)
    whatsapp_template = models.TextField(blank=True, default="")
    email_template = models.TextField(blank=True, default="")
    sms_template = models.TextField(blank=True, default="")
    push_template = models.TextField(blank=True, default="")
    sales_script_template = models.TextField(blank=True, default="")
    voice_script_template = models.TextField(blank=True, default="")
    facebook_template = models.TextField(blank=True, default="")
    instagram_template = models.TextField(blank=True, default="")
    language = models.CharField(max_length=20, default="en")
    variables = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_templates"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class Campaign(TenantModel):
    class Statuses(models.TextChoices):
        DRAFT = "Draft", "Draft"
        ACTIVE = "Active", "Active"
        SCHEDULED = "Scheduled", "Scheduled"
        RUNNING = "Running", "Running"
        COMPLETED = "Completed", "Completed"
        FAILED = "Failed", "Failed"
        PAUSED = "Paused", "Paused"
        CANCELLED = "Cancelled", "Cancelled"

    class CampaignType(models.TextChoices):
        PROJECT_LAUNCH = "PROJECT_LAUNCH", "Project Launch"
        PRICE_UPDATE = "PRICE_UPDATE", "Price Update"
        FESTIVAL_OFFER = "FESTIVAL_OFFER", "Festival Offer"
        INVENTORY_UPDATE = "INVENTORY_UPDATE", "Inventory Update"
        GENERAL_ANNOUNCEMENT = "GENERAL_ANNOUNCEMENT", "General Announcement"
        CUSTOM = "CUSTOM", "Custom"

    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=255, blank=True, default="")
    campaign_type = models.CharField(max_length=30, choices=CampaignType.choices, default=CampaignType.GENERAL_ANNOUNCEMENT)
    project = models.ForeignKey("properties.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_campaigns")
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.DRAFT)
    target_type = models.CharField(max_length=50, blank=True, default="AI_MATCHED")
    selected_customer_ids = models.JSONField(default=list, blank=True)
    reach = models.CharField(max_length=50, blank=True, default="0")
    total_sent = models.IntegerField(default=0)
    open_rate = models.FloatField(default=0.0)
    click_rate = models.FloatField(default=0.0)
    conversion_rate = models.FloatField(default=0.0)
    image_url = models.URLField(max_length=500, blank=True, default="")
    content = models.TextField(blank=True, default="")
    audience_segment = models.ForeignKey(AudienceSegment, on_delete=models.SET_NULL, null=True, blank=True, related_name="campaigns")
    contact_list = models.ForeignKey(ContactList, on_delete=models.SET_NULL, null=True, blank=True, related_name="campaigns")
    channels = models.JSONField(default=list, blank=True)
    ai_prompt = models.TextField(blank=True, default="")
    message_versions = models.JSONField(default=dict, blank=True)
    schedule_time = models.DateTimeField(null=True, blank=True)
    recurring = models.BooleanField(default=False)
    timezone = models.CharField(max_length=50, blank=True, default="UTC")
    total_reach = models.IntegerField(default=0)
    delivered = models.IntegerField(default=0)
    opened = models.IntegerField(default=0)
    clicked = models.IntegerField(default=0)
    replied = models.IntegerField(default=0)
    interested = models.IntegerField(default=0)
    site_visits = models.IntegerField(default=0)
    calls_booked = models.IntegerField(default=0)
    meetings = models.IntegerField(default=0)
    bookings = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_campaigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.status})"


class CampaignMessage(TenantModel):
    class MessageStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SENT = "SENT", "Sent"
        DELIVERED = "DELIVERED", "Delivered"
        OPENED = "OPENED", "Opened"
        CLICKED = "CLICKED", "Clicked"
        FAILED = "FAILED", "Failed"
        REPLIED = "REPLIED", "Replied"

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="messages")
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50, blank=True, default="")
    customer_email = models.EmailField(blank=True, default="")
    channel = models.CharField(max_length=30)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING)
    delivery_time = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    replied_at = models.DateTimeField(null=True, blank=True)
    reply_content = models.TextField(blank=True, default="")
    failed_reason = models.TextField(blank=True, default="")
    booking = models.BooleanField(default=False)
    booking_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campaign.name} → {self.customer_name} ({self.channel})"


class CampaignLog(TenantModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="broadcast_logs"
    )
    status = models.CharField(max_length=20, default="INFO")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.campaign.name} - {self.action}"


class CampaignAnalytics(TenantModel):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name="analytics")
    daily_stats = models.JSONField(default=dict, blank=True)
    hourly_stats = models.JSONField(default=dict, blank=True)
    city_stats = models.JSONField(default=dict, blank=True)
    builder_stats = models.JSONField(default=dict, blank=True)
    campaign_stats = models.JSONField(default=dict, blank=True)
    ai_recommendations = models.JSONField(default=dict, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Campaign Analytics"

    def __str__(self):
        return f"{self.campaign.name} - Analytics"