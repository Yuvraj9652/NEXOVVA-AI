from django.db import models
from django.conf import settings
from apps.common.models import TenantModel


class Note(TenantModel):
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="authored_notes")
    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="contact_notes"
    )
    deal = models.ForeignKey(
        "pipeline.Deal", on_delete=models.SET_NULL, null=True, blank=True, related_name="deal_notes"
    )
    lead = models.ForeignKey(
        "leads.Lead", on_delete=models.SET_NULL, null=True, blank=True, related_name="lead_notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note by {self.author.username} on {self.created_at.strftime('%Y-%m-%d')}"
