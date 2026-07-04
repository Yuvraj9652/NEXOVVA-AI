from django.db import models
from apps.common.models import TenantModel


class Project(TenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Unit(TenantModel):
    class Statuses(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        SOLD = "SOLD", "Sold"

    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="units")
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2)
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)
    area_sqft = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=Statuses.choices, default=Statuses.AVAILABLE)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - ${self.price}"


class PropertyImage(TenantModel):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="properties/")
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.unit.name} ({'Primary' if self.is_primary else 'Secondary'})"
