from django.contrib import admin
from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerRequirement,
    CustomerSource,
    CustomerDocument,
    CustomerNote,
    CustomerActivity,
    CustomerCategory,
    CustomerList,
    CustomerListCustomer,
)


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["customer_code", "first_name", "last_name", "email", "phone", "lead_status", "assigned_employee", "created_at"]
    list_filter = ["lead_status", "priority", "source_type", "created_at"]
    search_fields = ["customer_code", "first_name", "last_name", "email", "phone"]


admin.site.register(CustomerAddress)
admin.site.register(CustomerRequirement)
admin.site.register(CustomerSource)
admin.site.register(CustomerDocument)
admin.site.register(CustomerNote)
admin.site.register(CustomerActivity)
admin.site.register(CustomerCategory)
admin.site.register(CustomerList)
admin.site.register(CustomerListCustomer)
