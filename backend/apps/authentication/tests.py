import re
from datetime import timedelta
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from django.test import SimpleTestCase, TestCase
from django.utils import timezone
from django.core import mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.urls import reverse
from allauth.socialaccount.models import SocialApp
import config.settings.base as base_settings
from rest_framework.exceptions import ValidationError

from apps.authentication.services import AuthService
from apps.authentication.models import PendingRegistration, PasswordResetToken
from apps.accounts.models import Profile, UserProfile
from apps.organizations.models import Organization

User = get_user_model()


class EmailSettingsTests(SimpleTestCase):
    def test_email_backend_is_smtp_by_default(self):
        self.assertEqual(
            base_settings.EMAIL_BACKEND,
            "django.core.mail.backends.smtp.EmailBackend",
        )


class AuthenticationTests(TestCase):
    def setUp(self):
        site = Site.objects.get_or_create(id=1, defaults={"domain": "localhost", "name": "localhost"})[0]
        SocialApp.objects.filter(provider="google").delete()
        SocialApp.objects.create(
            provider="google",
            name="Google",
            client_id="test-client-id",
            secret="test-secret",
            key="",
        ).sites.add(site)

        self.register_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "Password123!",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "+1234567890",
            "organization_name": "Test Organization",
        }

    def test_google_login_redirects_directly_to_google_oauth(self):
        response = self.client.get(reverse("google_login_redirect"), follow=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn("https://accounts.google.com/o/oauth2/v2/auth", response.url)

        parsed = urlparse(response.url)
        query = parse_qs(parsed.query)
        self.assertEqual(query["response_type"], ["code"])
        self.assertEqual(query["client_id"], ["test-client-id"])
        self.assertEqual(query["redirect_uri"], ["http://testserver/api/auth/google/callback/"])
        self.assertIn("state", query)
        self.assertTrue(query["state"][0])

    @patch("apps.authentication.views.GoogleOAuth2Adapter.complete_login")
    @patch("allauth.socialaccount.providers.oauth2.client.OAuth2Client.get_access_token")
    @patch("apps.authentication.services.AuthService.handle_social_login")
    @patch("apps.authentication.views.complete_social_login")
    def test_google_login_callback_success(self, mock_complete_social_login, mock_handle_social_login, mock_get_access_token, mock_complete_login):
        # Setup mock user and token returned
        mock_get_access_token.return_value = {"access_token": "mock-access-token"}
        
        from unittest.mock import MagicMock
        mock_social_login = MagicMock()
        mock_user = User.objects.create_user(
            username="googlecallbackuser",
            email="googlecallbackuser@gmail.com",
            password="Password123!"
        )
        mock_social_login.user = mock_user
        mock_complete_login.return_value = mock_social_login
        
        mock_handle_social_login.return_value = {
            "access": "mock-jwt-access",
            "refresh": "mock-jwt-refresh"
        }
        
        # Call the callback endpoint
        response = self.client.get(
            reverse("google_login_callback"),
            {"code": "mock-auth-code", "state": "mock-state"},
            follow=False
        )
        
        # Verify it redirects to the frontend with tokens
        self.assertEqual(response.status_code, 302)
        self.assertIn("http://localhost:3000/oauth-callback", response.url)
        self.assertIn("access=mock-jwt-access", response.url)
        self.assertIn("refresh=mock-jwt-refresh", response.url)

    def test_registration_creates_pending_only(self):
        # Clean outbox
        mail.outbox = []
        
        pending = AuthService.register(self.register_data)
        
        # Verify no User is created yet
        self.assertFalse(User.objects.filter(username="testuser").exists())
        
        # Verify PendingRegistration is created
        self.assertTrue(PendingRegistration.objects.filter(username="testuser").exists())
        self.assertEqual(pending.email, "testuser@example.com")
        self.assertEqual(len(pending.otp_code), 64)  # SHA-256 hash length
        
        # Verify email is sent with 6-digit OTP
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        otp_match = re.search(r"\b\d{6}\b", email_body)
        self.assertIsNotNone(otp_match)

    def test_otp_verification_creates_user_and_org(self):
        mail.outbox = []
        AuthService.register(self.register_data)
        
        # Extract OTP from email
        email_body = mail.outbox[0].body
        otp_code = re.search(r"\b\d{6}\b", email_body).group()
        
        # Verify OTP
        result = AuthService.verify_otp({
            "email": "testuser@example.com",
            "otp_code": otp_code
        })
        
        # Verify tokens are generated
        self.assertIn("access", result)
        self.assertIn("refresh", result)
        
        # Verify User and Profile are created
        self.assertTrue(User.objects.filter(username="testuser").exists())
        user = User.objects.get(username="testuser")
        self.assertTrue(user.is_email_verified)
        
        # Verify Organization and Admin role are configured
        user_profile = UserProfile.objects.get(user=user)
        self.assertEqual(user_profile.role, UserProfile.Roles.ADMIN)
        self.assertEqual(user_profile.organization.name, "Test Organization")
        
        # Verify PendingRegistration is cleaned up
        self.assertFalse(PendingRegistration.objects.filter(username="testuser").exists())

    def test_otp_verification_failure_and_limit(self):
        mail.outbox = []
        AuthService.register(self.register_data)
        
        # Try invalid OTP code
        for i in range(5):
            with self.assertRaises(ValidationError) as context:
                AuthService.verify_otp({
                    "email": "testuser@example.com",
                    "otp_code": "000000"
                })
            self.assertIn("Invalid verification code.", str(context.exception))
            
        # The 6th attempt should fail and indicate that maximum attempts were exceeded / record deleted
        with self.assertRaises(ValidationError) as context:
            AuthService.verify_otp({
                "email": "testuser@example.com",
                "otp_code": "000000"
            })
        self.assertIn("Maximum verification attempts exceeded.", str(context.exception))
        
        # Pending registration must be deleted now
        self.assertFalse(PendingRegistration.objects.filter(username="testuser").exists())

    def test_resend_otp_cooldown_and_limit(self):
        mail.outbox = []
        pending = AuthService.register(self.register_data)
        
        # Immediate resend should raise cooldown ValidationError
        with self.assertRaises(ValidationError) as context:
            AuthService.resend_otp("testuser@example.com")
        self.assertIn("wait 60 seconds", str(context.exception))
        
        # Artificially bypass cooldown for tests
        pending.last_resend_at = timezone.now() - timedelta(seconds=65)
        pending.save()
        
        # Second send (resend 1)
        AuthService.resend_otp("testuser@example.com")
        self.assertEqual(len(mail.outbox), 2)
        
        # Third send (resend 2)
        pending.refresh_from_db()
        pending.last_resend_at = timezone.now() - timedelta(seconds=65)
        pending.save()
        AuthService.resend_otp("testuser@example.com")
        self.assertEqual(len(mail.outbox), 3)

        # Fourth send (resend 3)
        pending.refresh_from_db()
        pending.last_resend_at = timezone.now() - timedelta(seconds=65)
        pending.save()
        AuthService.resend_otp("testuser@example.com")
        self.assertEqual(len(mail.outbox), 4)
        
        # Fifth send (resend 4) - this should reach max limit
        pending.refresh_from_db()
        pending.last_resend_at = timezone.now() - timedelta(seconds=65)
        pending.save()
        with self.assertRaises(ValidationError) as context:
            AuthService.resend_otp("testuser@example.com")
        self.assertIn("Maximum resend limit reached.", str(context.exception))
        
        # Record must be deleted
        self.assertFalse(PendingRegistration.objects.filter(username="testuser").exists())

    def test_forgot_and_reset_password_otp(self):
        mail.outbox = []
        AuthService.register(self.register_data)
        
        # Verify first to create a real User
        email_body = mail.outbox[0].body
        otp_code = re.search(r"\b\d{6}\b", email_body).group()
        AuthService.verify_otp({
            "email": "testuser@example.com",
            "otp_code": otp_code
        })
        
        # Request forgot password OTP
        mail.outbox = []
        AuthService.forgot_password("testuser@example.com")
        
        # Retrieve reset OTP
        self.assertEqual(len(mail.outbox), 1)
        reset_body = mail.outbox[0].body
        reset_otp = re.search(r"\b\d{6}\b", reset_body).group()
        
        # Verify Reset OTP View check
        AuthService.verify_reset_otp({
            "email": "testuser@example.com",
            "otp_code": reset_otp
        })
        
        # Reset password
        AuthService.reset_password({
            "email": "testuser@example.com",
            "otp_code": reset_otp,
            "new_password": "NewSecurePassword123!"
        })
        
        # Verify login works with new password
        result = AuthService.login({
            "username": "testuser",
            "password": "NewSecurePassword123!"
        })
        self.assertIn("access", result)

    def test_social_login_handler_creates_profile(self):
        # Create user manually
        user = User.objects.create_user(
            username="googleuser",
            email="googleuser@gmail.com",
            password="GooglePassword123!"
        )
        
        # Run social login handler
        tokens = AuthService.handle_social_login(user)
        self.assertIn("access", tokens)
        
        # Verify email was automatically marked verified
        user.refresh_from_db()
        self.assertTrue(user.is_email_verified)
        
        # Profile must exist
        profile = Profile.objects.get(user=user)
        self.assertIsNotNone(profile)
