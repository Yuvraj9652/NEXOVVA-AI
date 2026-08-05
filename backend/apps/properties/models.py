from django.db import models
from apps.common.models import TenantModel


class Project(TenantModel):
    class ProjectStatus(models.TextChoices):
        PAST = "PAST", "Past"
        ONGOING = "ONGOING", "Ongoing"
        UPCOMING = "UPCOMING", "Upcoming"
        DRAFT = "DRAFT", "Draft"
        ARCHIVED = "ARCHIVED", "Archived"

    class PropertyType(models.TextChoices):
        APARTMENT = "APARTMENT", "Apartment"
        VILLA = "VILLA", "Villa"
        PLOT = "PLOT", "Plot"
        COMMERCIAL = "COMMERCIAL", "Commercial"
        PENTHOUSE = "PENTHOUSE", "Penthouse"
        TOWNHOUSE = "TOWNHOUSE", "Townhouse"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    short_description = models.TextField(blank=True, default="")
    seo_description = models.TextField(blank=True, default="")
    whatsapp_description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.DRAFT)
    builder = models.CharField(max_length=255, blank=True, default="")
    builder_logo = models.ImageField(upload_to="builders/", null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True, default="")
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, blank=True, default="")
    configurations = models.JSONField(default=list, blank=True)
    country = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    area = models.CharField(max_length=100, blank=True, default="")
    address = models.TextField(blank=True, default="")
    google_map_url = models.URLField(blank=True, default="")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    nearby_metro = models.CharField(max_length=255, blank=True, default="")
    nearby_schools = models.JSONField(default=list, blank=True)
    nearby_hospitals = models.JSONField(default=list, blank=True)
    nearby_malls = models.JSONField(default=list, blank=True)
    nearby_airport = models.CharField(max_length=255, blank=True, default="")
    towers = models.IntegerField(null=True, blank=True)
    floors = models.IntegerField(null=True, blank=True)
    total_units = models.IntegerField(null=True, blank=True)
    sizes_sqft = models.JSONField(default=list, blank=True)
    possession_date = models.DateField(null=True, blank=True)
    rera_number = models.CharField(max_length=100, blank=True, default="")
    starting_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    price_per_sqft = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    booking_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    payment_plan = models.TextField(blank=True, default="")
    ai_processed = models.BooleanField(default=False)
    ai_generated_keywords = models.JSONField(default=list, blank=True)
    ai_generated_tags = models.JSONField(default=list, blank=True)
    ai_generated_highlights = models.JSONField(default=list, blank=True)
    ai_generated_investment_points = models.JSONField(default=list, blank=True)
    ai_generated_summary = models.TextField(blank=True, default="")
    rera_approved = models.BooleanField(default=False)
    pet_friendly = models.BooleanField(default=False)
    ready_possession = models.BooleanField(default=False)
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    created_by = models.ForeignKey(
        "accounts.CustomUser", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

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
