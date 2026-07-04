from django.db import models
from apps.common.models import TenantModel


class Lead(TenantModel):
    class Statuses(models.TextChoices):
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        QUALIFIED = "QUALIFIED", "Qualified"
        UNQUALIFIED = "UNQUALIFIED", "Unqualified"
        LOST = "LOST", "Lost"

    class Sources(models.TextChoices):
        WEBSITE = "WEBSITE", "Website"
        REFERRAL = "REFERRAL", "Referral"
        COLD_CALL = "COLD_CALL", "Cold Call"
        ADVERTISEMENT = "ADVERTISEMENT", "Advertisement"
        OTHER = "OTHER", "Other"

    contact = models.ForeignKey(
        "contacts.Contact", on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    company = models.ForeignKey(
        "companies.Company", on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=Statuses.choices, default=Statuses.NEW
    )
    source = models.CharField(
        max_length=20, choices=Sources.choices, default=Sources.OTHER
    )
    budget = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    score = models.IntegerField(default=50)  # AI lead score (0-100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.status}"
