import uuid
from django.db import models
from django.conf import settings
from apps.common.models import TenantModel


class ProjectCategory(TenantModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    color = models.CharField(max_length=20, default="#14b8a6")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["organization", "name"]

    def __str__(self):
        return self.name


class ProjectMedia(TenantModel):
    class MediaType(models.TextChoices):
        IMAGE = "IMAGE", "Image"
        VIDEO = "VIDEO", "Video"
        VIRTUAL_TOUR = "VIRTUAL_TOUR", "Virtual Tour"
        DRONE_VIDEO = "DRONE_VIDEO", "Drone Video"
        FLOOR_PLAN = "FLOOR_PLAN", "Floor Plan"
        LOGO = "LOGO", "Logo"

    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="media")
    media_type = models.CharField(max_length=20, choices=MediaType.choices)
    file = models.FileField(upload_to="project_media/")
    thumbnail = models.ImageField(upload_to="project_media/thumbnails/", null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True, default="")
    is_primary = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.get_media_type_display()}"


class ProjectDocument(TenantModel):
    class DocumentType(models.TextChoices):
        PDF = "PDF", "PDF"
        CSV = "CSV", "CSV"
        DOCX = "DOCX", "DOCX"
        EXCEL = "EXCEL", "Excel"
        BROCHURE = "BROCHURE", "Brochure"
        PRICE_SHEET = "PRICE_SHEET", "Price Sheet"
        PAYMENT_PLAN = "PAYMENT_PLAN", "Payment Plan"
        LEGAL_DOC = "LEGAL_DOC", "Legal Docs"
        FLOOR_PLAN = "FLOOR_PLAN", "Floor Plans"
        OTHER = "OTHER", "Other"

    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="kb_documents", null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="project_documents/")
    file_size = models.BigIntegerField(default=0)
    version = models.PositiveIntegerField(default=1)
    processed = models.BooleanField(default=False)
    extracted_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.name} (v{self.version})"


class ProjectAmenity(TenantModel):
    class AmenityType(models.TextChoices):
        SWIMMING_POOL = "SWIMMING_POOL", "Swimming Pool"
        GYM = "GYM", "Gym"
        GARDEN = "GARDEN", "Garden"
        CLUB_HOUSE = "CLUB_HOUSE", "Club House"
        KIDS_PLAY_AREA = "KIDS_PLAY_AREA", "Kids Play Area"
        PARKING = "PARKING", "Parking"
        SECURITY = "SECURITY", "Security"
        POWER_BACKUP = "POWER_BACKUP", "Power Backup"
        LIFT = "LIFT", "Lift"
        CCTV = "CCTV", "CCTV"
        CUSTOM = "CUSTOM", "Custom"

    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="amenities")
    amenity_type = models.CharField(max_length=30, choices=AmenityType.choices)
    custom_name = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(blank=True, default="")
    icon = models.CharField(max_length=50, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["amenity_type"]
        unique_together = ["organization", "project", "amenity_type"]

    def __str__(self):
        return f"{self.project.name} - {self.get_amenity_type_display()}"


class ProjectVersion(TenantModel):
    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="versions")
    version_number = models.PositiveIntegerField()
    change_summary = models.TextField()
    changed_fields = models.JSONField(default=list, blank=True)
    snapshot = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-version_number"]
        unique_together = ["organization", "project", "version_number"]

    def __str__(self):
        return f"{self.project.name} - v{self.version_number}"


class ProjectAnalytics(TenantModel):
    project = models.OneToOneField("properties.Project", on_delete=models.CASCADE, related_name="kb_analytics")
    interested_customers = models.IntegerField(default=0)
    ai_recommendations = models.IntegerField(default=0)
    brochure_downloads = models.IntegerField(default=0)
    video_views = models.IntegerField(default=0)
    site_visits = models.IntegerField(default=0)
    bookings = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Project Analytics"

    def __str__(self):
        return f"{self.project.name} - Analytics"


class ProjectTag(TenantModel):
    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="kb_tags")
    name = models.CharField(max_length=50)
    color = models.CharField(max_length=20, default="#14b8a6")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        unique_together = ["organization", "project", "name"]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class ProjectFAQ(TenantModel):
    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=255)
    answer = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "question"]
        verbose_name = "Project FAQ"
        verbose_name_plural = "Project FAQs"

    def __str__(self):
        return f"{self.project.name} - {self.question[:50]}"


class ProjectHighlight(TenantModel):
    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="highlights")
    text = models.CharField(max_length=255)
    icon = models.CharField(max_length=50, blank=True, default="")
    sort_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.project.name} - {self.text[:50]}"


class ProjectProcessingJob(TenantModel):
    class JobStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="processing_jobs")
    job_type = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=JobStatus.choices, default=JobStatus.PENDING)
    progress = models.IntegerField(default=0)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name} - {self.job_type} ({self.get_status_display()})"


class ProjectChatSession(TenantModel):
    project = models.ForeignKey("properties.Project", on_delete=models.CASCADE, related_name="chat_sessions")
    session_id = models.UUIDField(default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Chat")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="project_chat_sessions"
    )
    status = models.CharField(max_length=20, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.project.name} - {self.title}"


class ProjectChatMessage(models.Model):
    session = models.ForeignKey(ProjectChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=[("user", "User"), ("assistant", "Assistant")])
    content = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.session.title} - {self.role}: {self.content[:50]}"
