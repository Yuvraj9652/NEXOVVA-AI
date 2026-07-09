from django.contrib import admin
from .models import PendingRegistration, PasswordResetToken


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "organization_name", "otp_expires_at", "verification_attempts", "resend_count", "created_at"]
    list_filter = ["created_at", "otp_expires_at"]
    search_fields = ["email", "username", "organization_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        (None, {"fields": ("username", "email", "password", "first_name", "last_name", "phone_number", "organization_name")}),
        ("OTP Settings", {"fields": ("otp_code", "otp_expires_at", "verification_attempts", "resend_count", "last_resend_at")}),
        ("Metadata", {"fields": ("id", "created_at")}),
    )


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ["user", "expires_at", "is_used", "verification_attempts", "created_at"]
    list_filter = ["is_used", "created_at", "expires_at"]
    search_fields = ["user__username", "user__email"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at"]
    fieldsets = (
        (None, {"fields": ("user", "otp_code", "expires_at", "is_used", "verification_attempts")}),
        ("Metadata", {"fields": ("id", "created_at")}),
    )
