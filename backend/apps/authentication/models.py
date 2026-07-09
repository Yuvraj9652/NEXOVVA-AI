import uuid
from django.db import models
from django.conf import settings


class PendingRegistration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store the pre-hashed password
    first_name = models.CharField(max_length=150, blank=True, default="")
    last_name = models.CharField(max_length=150, blank=True, default="")
    phone_number = models.CharField(max_length=20, blank=True, default="")
    organization_name = models.CharField(max_length=255)
    otp_code = models.CharField(max_length=255)  # SHA-256 hash of the secure 6-digit OTP
    otp_expires_at = models.DateTimeField()
    verification_attempts = models.IntegerField(default=0)  # Max 5 attempts
    resend_count = models.IntegerField(default=0)  # Max 3 resends
    last_resend_at = models.DateTimeField(null=True, blank=True)  # Cooldown check
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending Registration for {self.email} ({self.username})"


class PasswordResetToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_resets"
    )
    otp_code = models.CharField(max_length=255)  # SHA-256 hash of the secure 6-digit OTP
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    verification_attempts = models.IntegerField(default=0)  # Max 5 attempts
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password Reset OTP for {self.user.email} (Used: {self.is_used})"
