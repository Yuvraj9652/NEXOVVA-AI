from django.contrib import admin
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


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "organization", "is_active", "created_at"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "description"]


@admin.register(ProjectMedia)
class ProjectMediaAdmin(admin.ModelAdmin):
    list_display = ["project", "media_type", "is_primary", "created_at"]
    list_filter = ["media_type", "is_primary"]
    search_fields = ["project__name", "caption"]


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ["project", "name", "document_type", "version", "processed", "created_at"]
    list_filter = ["document_type", "processed"]
    search_fields = ["project__name", "name"]


@admin.register(ProjectAmenity)
class ProjectAmenityAdmin(admin.ModelAdmin):
    list_display = ["project", "amenity_type", "custom_name"]
    list_filter = ["amenity_type"]
    search_fields = ["project__name", "custom_name"]


@admin.register(ProjectVersion)
class ProjectVersionAdmin(admin.ModelAdmin):
    list_display = ["project", "version_number", "change_summary", "created_by", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["project__name", "change_summary"]


@admin.register(ProjectAnalytics)
class ProjectAnalyticsAdmin(admin.ModelAdmin):
    list_display = ["project", "interested_customers", "bookings", "revenue", "conversion_rate", "updated_at"]


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ["project", "name", "color"]
    search_fields = ["project__name", "name"]


@admin.register(ProjectFAQ)
class ProjectFAQAdmin(admin.ModelAdmin):
    list_display = ["project", "question", "is_ai_generated", "sort_order"]
    list_filter = ["is_ai_generated"]
    search_fields = ["project__name", "question"]


@admin.register(ProjectHighlight)
class ProjectHighlightAdmin(admin.ModelAdmin):
    list_display = ["project", "text", "sort_order"]


@admin.register(ProjectProcessingJob)
class ProjectProcessingJobAdmin(admin.ModelAdmin):
    list_display = ["project", "job_type", "status", "progress", "created_at"]
    list_filter = ["job_type", "status"]


@admin.register(ProjectChatSession)
class ProjectChatSessionAdmin(admin.ModelAdmin):
    list_display = ["project", "title", "created_by", "status", "created_at"]


@admin.register(ProjectChatMessage)
class ProjectChatMessageAdmin(admin.ModelAdmin):
    list_display = ["session", "role", "content_preview", "created_at"]
    list_filter = ["role", "created_at"]

    def content_preview(self, obj):
        return obj.content[:80]
