from django.db import models
from apps.common.models import TenantModel


class Customer(TenantModel):
    class LeadStatus(models.TextChoices):
        HOT = "HOT", "Hot Lead"
        WARM = "WARM", "Warm Lead"
        COLD = "COLD", "Cold Lead"
        NEW = "NEW", "New"
        CONTACTED = "CONTACTED", "Contacted"
        VISITED = "VISITED", "Visited"
        NEGOTIATION = "NEGOTIATION", "In Negotiation"
        BOOKED = "BOOKED", "Booked"
        CLOSED = "CLOSED", "Closed"
        LOST = "LOST", "Lost"

    class Priority(models.TextChoices):
        HIGH = "HIGH", "High"
        MEDIUM = "MEDIUM", "Medium"
        LOW = "LOW", "Low"

    class SourceType(models.TextChoices):
        WEBSITE = "WEBSITE", "Website"
        WHATSAPP = "WHATSAPP", "WhatsApp"
        FACEBOOK_ADS = "FACEBOOK_ADS", "Facebook Ads"
        INSTAGRAM = "INSTAGRAM", "Instagram"
        GOOGLE_ADS = "GOOGLE_ADS", "Google Ads"
        REFERRAL = "REFERRAL", "Referral"
        BROKER = "BROKER", "Broker"
        WALK_IN = "WALK_IN", "Walk-in"
        SALES_EXECUTIVE = "SALES_EXECUTIVE", "Sales Executive"
        CSV_IMPORT = "CSV_IMPORT", "CSV Import"
        EXISTING_CUSTOMER = "EXISTING_CUSTOMER", "Existing Customer"
        OTHER = "OTHER", "Other"

    customer_code = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=50, blank=True, default="")
    alternate_phone = models.CharField(max_length=50, blank=True, default="")
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[("MALE", "Male"), ("FEMALE", "Female"), ("OTHER", "Other")], blank=True, default="")
    occupation = models.CharField(max_length=150, blank=True, default="")
    company = models.CharField(max_length=255, blank=True, default="")
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    photo = models.ImageField(upload_to="customers/photos/", null=True, blank=True)
    lead_status = models.CharField(max_length=20, choices=LeadStatus.choices, default=LeadStatus.NEW)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    tags = models.JSONField(default=list, blank=True)
    is_archived = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    assigned_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_customers",
    )
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_customers",
    )
    source_type = models.CharField(max_length=30, choices=SourceType.choices, blank=True, default="")
    source_notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.customer_code or self.id})"

    def save(self, *args, **kwargs):
        if not self.customer_code:
            from django.db.models import Max
            last_id = Customer.objects.aggregate(Max("id"))["id__max"]
            next_id = (last_id + 1) if last_id else 1
            self.customer_code = f"CUS-{next_id:06d}"
        super().save(*args, **kwargs)


class CustomerAddress(TenantModel):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="address")
    country = models.CharField(max_length=100, blank=True, default="")
    state = models.CharField(max_length=100, blank=True, default="")
    city = models.CharField(max_length=100, blank=True, default="")
    area = models.CharField(max_length=150, blank=True, default="")
    address = models.TextField(blank=True, default="")
    pincode = models.CharField(max_length=10, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Address for {self.customer}"


class CustomerRequirement(TenantModel):
    class Purpose(models.TextChoices):
        INVESTMENT = "INVESTMENT", "Investment"
        SELF_USE = "SELF_USE", "Self Use"
        RENTAL = "RENTAL", "Rental"

    class PropertyType(models.TextChoices):
        APARTMENT = "APARTMENT", "Apartment"
        VILLA = "VILLA", "Villa"
        PLOT = "PLOT", "Plot"
        OFFICE = "OFFICE", "Office"
        SHOP = "SHOP", "Shop"
        COMMERCIAL = "COMMERCIAL", "Commercial"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="requirements")
    purpose = models.CharField(max_length=20, choices=Purpose.choices, blank=True, default="")
    property_type = models.CharField(max_length=20, choices=PropertyType.choices, blank=True, default="")
    configuration = models.JSONField(default=list, blank=True)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_city = models.CharField(max_length=100, blank=True, default="")
    preferred_area = models.CharField(max_length=150, blank=True, default="")
    preferred_builder = models.CharField(max_length=255, blank=True, default="")
    loan_required = models.BooleanField(default=False)
    parking_required = models.BooleanField(default=False)
    possession_preference = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Requirement for {self.customer}"


class CustomerSource(TenantModel):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="source_detail")
    source_type = models.CharField(max_length=30, choices=Customer.SourceType.choices, blank=True, default="")
    added_by_employee = models.ForeignKey(
        "employees.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_sources",
    )
    added_by_name = models.CharField(max_length=255, blank=True, default="")
    employee_id_display = models.CharField(max_length=50, blank=True, default="")
    department = models.CharField(max_length=150, blank=True, default="")
    role = models.CharField(max_length=100, blank=True, default="")
    referral_name = models.CharField(max_length=255, blank=True, default="")
    referral_phone = models.CharField(max_length=50, blank=True, default="")
    relationship = models.CharField(max_length=150, blank=True, default="")
    broker_name = models.CharField(max_length=255, blank=True, default="")
    broker_company = models.CharField(max_length=255, blank=True, default="")
    broker_phone = models.CharField(max_length=50, blank=True, default="")
    commission = models.CharField(max_length=50, blank=True, default="")
    campaign_name = models.CharField(max_length=255, blank=True, default="")
    landing_page = models.URLField(blank=True, default="")
    utm_source = models.CharField(max_length=150, blank=True, default="")
    utm_medium = models.CharField(max_length=150, blank=True, default="")
    utm_campaign = models.CharField(max_length=150, blank=True, default="")
    import_file = models.CharField(max_length=255, blank=True, default="")
    imported_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="imported_customers",
    )
    import_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Source for {self.customer}"


class CustomerDocument(TenantModel):
    class DocumentType(models.TextChoices):
        PAN = "PAN", "PAN"
        AADHAR = "AADHAR", "Aadhar"
        PASSPORT = "PASSPORT", "Passport"
        LOAN_PAPERS = "LOAN_PAPERS", "Loan Papers"
        AGREEMENT = "AGREEMENT", "Agreement"
        OTHER = "OTHER", "Other"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="documents")
    document_type = models.CharField(max_length=20, choices=DocumentType.choices, default=DocumentType.OTHER)
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_customer_docs",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_name} for {self.customer}"


class CustomerNote(TenantModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="notes")
    note = models.TextField()
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_notes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for {self.customer} at {self.created_at}"


class CustomerActivity(TenantModel):
    class ActivityType(models.TextChoices):
        CUSTOMER_CREATED = "CUSTOMER_CREATED", "Customer Created"
        BUDGET_UPDATED = "BUDGET_UPDATED", "Budget Updated"
        DOCUMENT_UPLOADED = "DOCUMENT_UPLOADED", "Document Uploaded"
        ASSIGNED = "ASSIGNED", "Customer Assigned"
        STATUS_CHANGED = "STATUS_CHANGED", "Status Changed"
        ARCHIVED = "ARCHIVED", "Customer Archived"
        RESTORED = "RESTORED", "Customer Restored"
        NOTE_ADDED = "NOTE_ADDED", "Note Added"
        CALL_LOGGED = "CALL_LOGGED", "Call Logged"
        MEETING = "MEETING", "Meeting"
        EMAIL = "EMAIL", "Email Sent"

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="activities")
    activity = models.CharField(max_length=100, choices=ActivityType.choices)
    description = models.TextField(blank=True, default="")
    performed_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_activities",
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.activity} for {self.customer}"


class CustomerCategory(TenantModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    color = models.CharField(max_length=20, blank=True, default="#6366f1")
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_categories",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CustomerList(TenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_lists",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    customer_count = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def update_count(self):
        self.customer_count = self.customers.count()
        self.save(update_fields=["customer_count"])


class CustomerListCustomer(TenantModel):
    customer_list = models.ForeignKey(CustomerList, on_delete=models.CASCADE, related_name="list_customers")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="customer_lists")

    class Meta:
        unique_together = ["customer_list", "customer"]

    def __str__(self):
        return f"{self.customer} in {self.customer_list}"
