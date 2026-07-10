from django.core.mail import send_mail
from django.conf import settings
from apps.accounts.models import CustomUser as User


class EmailService:
    @staticmethod
    def send_verification_email(user: User, otp_code: str) -> None:
        """Send email verification code containing the 6-digit numeric OTP."""
        subject = "Verify your email - NEXOVA AI"
        message = (
            f"Hi {user.username},\n\n"
            f"Thank you for registering at NEXOVA AI.\n"
            f"Please verify your email address by submitting the following OTP code:\n\n"
            f"{otp_code}\n\n"
            f"This code will expire in 10 minutes.\n\n"
            f"If you did not request this, please ignore this email.\n"
        )
        recipient_list = [user.email]
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nexova.ai"),
            recipient_list=recipient_list,
            fail_silently=False,
        )

    @staticmethod
    def send_password_reset_email(user: User, otp_code: str) -> None:
        """Send password reset OTP."""
        subject = "Reset your password - NEXOVA AI"
        message = (
            f"Hi {user.username},\n\n"
            f"We received a request to reset your password.\n"
            f"Please reset your password by submitting the following OTP code:\n\n"
            f"{otp_code}\n\n"
            f"This code will expire in 10 minutes.\n\n"
            f"If you did not request a password reset, please ignore this email.\n"
        )
        recipient_list = [user.email]
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nexova.ai"),
            recipient_list=recipient_list,
            fail_silently=False,
        )
