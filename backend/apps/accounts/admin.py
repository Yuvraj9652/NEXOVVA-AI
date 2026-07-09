from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile, Profile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ["username", "email", "phone_number", "is_email_verified", "is_phone_verified", "last_activity", "is_staff", "is_superuser"]
    list_filter = ["is_staff", "is_superuser", "is_active", "is_email_verified", "is_phone_verified"]
    search_fields = ["username", "first_name", "last_name", "email", "phone_number"]
    ordering = ["-date_joined"]
    readonly_fields = ["id", "created_at", "updated_at", "last_activity"]

    # Customize fieldsets to include new fields
    fieldsets = UserAdmin.fieldsets + (
        (
            "Verification & Activity",
            {
                "fields": (
                    "phone_number",
                    "is_email_verified",
                    "is_phone_verified",
                    "last_activity",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "role", "organization", "created_at"]
    list_filter = ["role", "created_at"]
    search_fields = ["user__username", "user__email", "organization__name"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        (None, {"fields": ("user", "organization", "role")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "gender", "location", "timezone", "language", "theme", "created_at"]
    list_filter = ["gender", "timezone", "language", "theme", "created_at"]
    search_fields = ["user__username", "user__email", "location", "bio"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at"]
    fieldsets = (
        ("User", {"fields": ("user", "avatar")}),
        ("Details", {"fields": ("bio", "date_of_birth", "gender", "location")}),
        ("Links", {"fields": ("website", "github", "linkedin")}),
        ("Preferences", {"fields": ("timezone", "language", "theme")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )