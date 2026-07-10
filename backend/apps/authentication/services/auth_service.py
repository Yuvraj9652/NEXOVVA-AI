import secrets
import hashlib
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from apps.accounts.models import Profile, UserProfile, CustomUser as User
from apps.organizations.models import Organization
from apps.authentication.models import PendingRegistration, PasswordResetToken
from apps.authentication.services.email_service import EmailService

def hash_otp(code: str) -> str:
    """Securely hash a numeric OTP code using SHA-256."""
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


class AuthService:
    @staticmethod
    def register(data: dict) -> PendingRegistration:
        """Validate and create a pending registration with a hashed password and hashed 6-digit OTP."""
        username = data["username"]
        email = data["email"]
        password = data["password"]
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        phone_number = data.get("phone_number", "")
        organization_name = data["organization_name"]

        # Clean up expired pending registrations first
        PendingRegistration.objects.filter(otp_expires_at__lt=timezone.now()).delete()

        # Check uniqueness against verified users
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError({"username": "A user with this username already exists."})
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "A user with this email already exists."})

        # Check uniqueness against active pending registrations
        if PendingRegistration.objects.filter(username__iexact=username).exists():
            raise ValidationError({"username": "A registration with this username is already pending."})
        if PendingRegistration.objects.filter(email__iexact=email).exists():
            raise ValidationError({"email": "A registration with this email is already pending."})

        # Securely hash password
        hashed_password = make_password(password)

        # Generate secure 6-digit numeric OTP
        otp_code = "".join(secrets.choice("0123456789") for _ in range(6))
        hashed_otp = hash_otp(otp_code)

        # Create PendingRegistration record
        pending = PendingRegistration.objects.create(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            organization_name=organization_name,
            otp_code=hashed_otp,
            otp_expires_at=timezone.now() + timedelta(minutes=10),
            last_resend_at=timezone.now(),
        )

        # Send OTP to email
        try:
            EmailService.send_verification_email(pending, otp_code)
        except Exception as e:
            # Clean up pending record so user can try again
            pending.delete()
            raise ValidationError({
                "email": f"Verification email could not be sent: {str(e)}. Please check your email settings."
            })

        return pending

    @staticmethod
    def verify_otp(data: dict) -> dict:
        """Verify the 6-digit OTP code. If valid, create User, Organization, Profile, and return tokens."""
        email = data.get("email")
        otp_code = data.get("otp_code")

        try:
            pending = PendingRegistration.objects.get(email__iexact=email)
        except PendingRegistration.DoesNotExist:
            raise ValidationError({"email": "No pending registration found for this email address."})

        # Check OTP expiration
        if pending.otp_expires_at < timezone.now():
            pending.delete()
            raise ValidationError({"otp_code": "The verification code has expired. Please register again."})

        # Increment verification attempts
        pending.verification_attempts += 1
        pending.save(update_fields=["verification_attempts"])

        # Check max attempts limit
        if pending.verification_attempts > 5:
            pending.delete()
            raise ValidationError({"otp_code": "Maximum verification attempts exceeded. Please register again."})

        # Verify OTP code
        if pending.otp_code != hash_otp(otp_code):
            raise ValidationError({"otp_code": "Invalid verification code."})

        # Create User, Organization, and setup Profiles in an atomic transaction
        with transaction.atomic():
            user = User.objects.create(
                username=pending.username,
                email=pending.email,
                password=pending.password,  # Password is already hashed
                first_name=pending.first_name,
                last_name=pending.last_name,
                phone_number=pending.phone_number,
                is_email_verified=True,
            )

            org = Organization.objects.create(name=pending.organization_name)

            # Setup UserProfile (signals handle basic creation, we configure org and role)
            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.organization = org
            user_profile.role = UserProfile.Roles.ADMIN
            user_profile.save(update_fields=["organization", "role"])

            # Clean up pending registration
            pending.delete()

        # Update last activity
        User.objects.filter(pk=user.pk).update(last_activity=timezone.now())

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user_profile.role,
                "organization": {
                    "id": str(org.id),
                    "name": org.name,
                    "slug": org.slug,
                }
            }
        }

    @staticmethod
    def resend_otp(email: str) -> None:
        """Resend OTP for pending registration, enforcing 60-second cooldown and 3-resend limit."""
        try:
            pending = PendingRegistration.objects.get(email__iexact=email)
        except PendingRegistration.DoesNotExist:
            raise ValidationError({"email": "No pending registration found for this email address."})

        # Check if expired
        if pending.otp_expires_at < timezone.now():
            pending.delete()
            raise ValidationError({"email": "Registration has expired. Please register again."})

        # Check resend limit
        if pending.resend_count >= 3:
            pending.delete()
            raise ValidationError({"email": "Maximum resend limit reached. Please register again."})

        # Check cooldown
        if pending.last_resend_at and timezone.now() - pending.last_resend_at < timedelta(seconds=60):
            raise ValidationError({"email": "Please wait 60 seconds before requesting a new OTP."})

        # Generate new 6-digit OTP
        otp_code = "".join(secrets.choice("0123456789") for _ in range(6))
        hashed_otp = hash_otp(otp_code)

        # Update pending registration
        pending.otp_code = hashed_otp
        pending.otp_expires_at = timezone.now() + timedelta(minutes=10)
        pending.verification_attempts = 0
        pending.resend_count += 1
        pending.last_resend_at = timezone.now()
        pending.save()

        # Send OTP
        try:
            EmailService.send_verification_email(pending, otp_code)
        except Exception as e:
            raise ValidationError({
                "email": f"Verification email could not be resent: {str(e)}. Please try again later."
            })

    @staticmethod
    def login(data: dict, request=None) -> dict:
        """Authenticate a user using username or email and password."""
        username_or_email = data.get("username") or data.get("email")
        password = data.get("password")

        # Find user
        if "@" in username_or_email:
            try:
                user = User.objects.get(email__iexact=username_or_email)
            except User.DoesNotExist:
                raise AuthenticationFailed("Invalid email or password.")
        else:
            try:
                user = User.objects.get(username__iexact=username_or_email)
            except User.DoesNotExist:
                raise AuthenticationFailed("Invalid username or password.")

        # Authenticate
        user_auth = authenticate(request=request, username=user.username, password=password)
        if not user_auth:
            raise AuthenticationFailed("Invalid credentials.")

        if not user.is_active:
            raise AuthenticationFailed("User account is disabled.")

        # Check if email is verified
        if not user.is_email_verified:
            raise ValidationError({"email": "Please verify your email address before logging in."})

        # Update last activity
        User.objects.filter(pk=user.pk).update(last_activity=timezone.now())

        # Check for confirmed MFA TOTP device
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from django.core import signing
        has_mfa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        if has_mfa:
            temp_token = signing.dumps({"user_id": str(user.id)}, salt="mfa-login")
            return {
                "mfa_required": True,
                "temp_token": temp_token,
            }

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        return {
            "mfa_required": False,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user_profile.role,
                "organization": {
                    "id": str(user_profile.organization.id) if user_profile.organization else None,
                    "name": user_profile.organization.name if user_profile.organization else None,
                    "slug": user_profile.organization.slug if user_profile.organization else None,
                } if user_profile.organization else None,
            }
        }

    @staticmethod
    def logout(refresh_token: str) -> None:
        """Blacklist the provided refresh token."""
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            raise ValidationError({"refresh": str(e)})

    @staticmethod
    def refresh(refresh_token: str) -> dict:
        """Rotate and return new access and refresh tokens using the refresh token."""
        try:
            refresh = RefreshToken(refresh_token)
            new_data = {
                "access": str(refresh.access_token),
            }
            if getattr(settings, "SIMPLE_JWT", {}).get("ROTATE_REFRESH_TOKENS", False):
                new_data["refresh"] = str(refresh)
            return new_data
        except TokenError as e:
            raise ValidationError({"refresh": str(e)})

    @staticmethod
    def forgot_password(email: str) -> None:
        """Generate a password reset OTP, hash it, and dispatch instructions via email."""
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "User with this email does not exist."})

        # Deactivate old password reset OTPs to prevent reuse
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)

        # Generate 6-digit reset OTP
        otp_code = "".join(secrets.choice("0123456789") for _ in range(6))
        hashed_otp = hash_otp(otp_code)
        PasswordResetToken.objects.create(
            user=user,
            otp_code=hashed_otp,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        # Send reset email
        try:
            EmailService.send_password_reset_email(user, otp_code)
        except Exception as e:
            PasswordResetToken.objects.filter(user=user, otp_code=hashed_otp).update(is_used=True)
            raise ValidationError({
                "email": f"Password reset email could not be sent: {str(e)}. Please try again later."
            })

    @staticmethod
    def verify_reset_otp(data: dict) -> None:
        """Validate reset OTP code without invalidating it (pre-reset check)."""
        email = data.get("email")
        otp_code = data.get("otp_code")

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise ValidationError({"email": "User with this email does not exist."})

        try:
            reset_token = PasswordResetToken.objects.filter(
                user=user,
                is_used=False
            ).latest("created_at")
        except PasswordResetToken.DoesNotExist:
            raise ValidationError({"otp_code": "No active password reset request found."})

        # Check expiration
        if reset_token.expires_at < timezone.now():
            raise ValidationError({"otp_code": "Password reset code has expired."})

        # Track attempts
        reset_token.verification_attempts += 1
        reset_token.save(update_fields=["verification_attempts"])

        if reset_token.verification_attempts > 5:
            reset_token.is_used = True
            reset_token.save(update_fields=["is_used"])
            raise ValidationError({"otp_code": "Maximum verification attempts exceeded. Please request a new OTP."})

        # Check code matching
        if reset_token.otp_code != hash_otp(otp_code):
            raise ValidationError({"otp_code": "Invalid password reset code."})

    @staticmethod
    def reset_password(data: dict) -> None:
        """Reset user password after validating email and reset OTP."""
        email = data.get("email")
        otp_code = data.get("otp_code")
        new_password = data.get("new_password")

        # Reuse verification method to track attempts & expiration
        AuthService.verify_reset_otp(data)

        # Retrieve user and token
        user = User.objects.get(email__iexact=email)
        reset_token = PasswordResetToken.objects.filter(user=user, is_used=False).latest("created_at")

        # Set new password
        user.set_password(new_password)
        user.save()

        # Invalidate OTP
        reset_token.is_used = True
        reset_token.save(update_fields=["is_used"])

    @staticmethod
    def change_password(user: User, data: dict) -> None:
        """Change the password of the authenticated user after checking their old password."""
        old_password = data.get("old_password")
        new_password = data.get("new_password")

        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Old password is incorrect."})

        user.set_password(new_password)
        user.save()

    @staticmethod
    def handle_social_login(user: User) -> dict:
        """Handle post-login logic for a social user: create/update profile and generate tokens."""
        if not user.is_email_verified:
            user.is_email_verified = True
            user.save(update_fields=["is_email_verified"])

        # Fetch social account details
        from allauth.socialaccount.models import SocialAccount
        social_account = SocialAccount.objects.filter(user=user, provider="google").first()

        avatar_url = ""
        if social_account:
            extra_data = social_account.extra_data
            user_updated = False
            if not user.first_name and extra_data.get("given_name"):
                user.first_name = extra_data.get("given_name")
                user_updated = True
            if not user.last_name and extra_data.get("family_name"):
                user.last_name = extra_data.get("family_name")
                user_updated = True
            if user_updated:
                user.save(update_fields=["first_name", "last_name"])

            avatar_url = extra_data.get("picture", "")

        # Get or create profile
        profile, _ = Profile.objects.get_or_create(user=user)
        if avatar_url and not profile.avatar:
            try:
                import requests
                from django.core.files.base import ContentFile
                response = requests.get(avatar_url, timeout=5)
                if response.status_code == 200:
                    profile.avatar.save(f"avatar_{user.id}.jpg", ContentFile(response.content), save=False)
            except Exception:
                pass

        profile.save()

        # Update last activity
        User.objects.filter(pk=user.pk).update(last_activity=timezone.now())

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
