from django.db import models
from apps.common.models import TenantModel


class Customer(TenantModel):
    class Segments(models.TextChoices):
        BUYER = "BUYER", "Buyer"
        TENANT = "TENANT", "Tenant"
        LANDLORD = "LANDLORD", "Landlord"
        CLIENT = "CLIENT", "Client"

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True, default="")
    segment = models.CharField(
        max_length=20, choices=Segments.choices, default=Segments.CLIENT
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.segment})"


class CustomerTimelineEvent(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="timeline_events")
    event_type = models.CharField(max_length=100)  # e.g., "call_logged", "meeting", "email"
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.customer.first_name} - {self.event_type} - {self.created_at}"
