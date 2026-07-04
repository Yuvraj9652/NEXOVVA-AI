from django.db import models
from apps.common.models import TenantModel


class Company(TenantModel):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, default="")
    industry = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
