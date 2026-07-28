from django.db import models
from apps.common.models import TenantModel


class Document(TenantModel):
    class Statuses(models.TextChoices):
        UPLOADING = "UPLOADING", "Uploading"
        EXTRACTING = "EXTRACTING", "Extracting"
        CHUNKING = "CHUNKING", "Chunking"
        EMBEDDING = "EMBEDDING", "Embedding"
        READY = "READY", "Ready"
        FAILED = "FAILED", "Failed"

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="documents/")
    extracted_text = models.TextField(blank=True, default="")
    version = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=Statuses.choices,
        default=Statuses.UPLOADING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} (v{self.version})"
