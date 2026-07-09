import uuid
import re
from datetime import date, timedelta
from django.utils import timezone
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import Profile, UserProfile
from apps.organizations.models import Organization
from apps.authentication.models import PendingRegistration, PasswordResetToken
from apps.authentication.services import AuthService, ProfileService

User = get_user_model()


class AuthenticationIntegrationTests(APITestCase):
    def test_user_registration_initiates_pending_registration(self):
        url = reverse("auth_register")
        data = {
            "username": "testagent",
            "email": "testagent@nexova.ai",
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "Agent",
            "phone_number": "+1234567890",
            "organization_name": "Nexova Realty",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Verify no User is created yet
        self.assertFalse(User.objects.filter(username="testagent").exists())

        # Verify PendingRegistration exists
        self.assertTrue(PendingRegistration.objects.filter(username="testagent").exists())
        pending = PendingRegistration.objects.get(username="testagent")
        self.assertEqual(pending.email, "testagent@nexova.ai")
        self.assertEqual(pending.phone_number, "+1234567890")

    def test_user_login_returns_token_and_user_details(self):
        # Register first
        register_url = reverse("auth_register")
        register_data = {
            "username": "testagent",
            "email": "testagent@nexova.ai",
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "Agent",
            "organization_name": "Nexova Realty",
        }
        self.client.post(register_url, register_data, format="json")

        # Manually create the user to bypass verify (representing verified user)
        user = User.objects.create_user(
            username="testagent",
            email="testagent@nexova.ai",
            password="SecurePassword123!",
            first_name="Test",
            last_name="Agent"
        )
        user.is_email_verified = True
        user.save()

        # Create Org and UserProfile
        org = Organization.objects.create(name="Nexova Realty")
        user_profile = UserProfile.objects.get(user=user)
        user_profile.organization = org
        user_profile.role = UserProfile.Roles.ADMIN
        user_profile.save()

        # Login
        login_url = reverse("auth_login")
        login_data = {
            "username": "testagent",
            "password": "SecurePassword123!",
        }

        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertIn("access", response.data["data"])
        self.assertIn("refresh", response.data["data"])
        self.assertIn("user", response.data["data"])
        self.assertEqual(response.data["data"]["user"]["username"], "testagent")
        self.assertEqual(response.data["data"]["user"]["role"], UserProfile.Roles.ADMIN)

        # Verify last activity updated
        user.refresh_from_db()
        self.assertIsNotNone(user.last_activity)

    def test_verify_otp_flow(self):
        from apps.authentication.services.auth_service import hash_otp
        otp_code = "123456"
        PendingRegistration.objects.create(
            username="verifyuser",
            email="verify@nexova.ai",
            password="SecurePassword123!",
            organization_name="Test Org",
            otp_code=hash_otp(otp_code),
            otp_expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse("auth_verify_otp")
        response = self.client.post(url, {"email": "verify@nexova.ai", "otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Check User created and email verified
        user = User.objects.get(username="verifyuser")
        self.assertTrue(user.is_email_verified)

        # Check PendingRegistration deleted
        self.assertFalse(PendingRegistration.objects.filter(email="verify@nexova.ai").exists())

    def test_resend_otp_flow(self):
        from apps.authentication.services.auth_service import hash_otp
        PendingRegistration.objects.create(
            username="resenduser",
            email="resend@nexova.ai",
            password="SecurePassword123!",
            organization_name="Test Org",
            otp_code=hash_otp("111111"),
            otp_expires_at=timezone.now() + timedelta(minutes=10),
            last_resend_at=timezone.now() - timedelta(seconds=65) # bypass cooldown
        )

        url = reverse("auth_resend_otp")
        response = self.client.post(url, {"email": "resend@nexova.ai"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Check new OTP code created
        pending = PendingRegistration.objects.get(email="resend@nexova.ai")
        self.assertNotEqual(pending.otp_code, hash_otp("111111"))

    def test_password_reset_flow(self):
        user = User.objects.create_user(
            username="resetuser",
            email="reset@nexova.ai",
            password="OldSecurePassword123!"
        )

        # 1. Forgot password request
        forgot_url = reverse("auth_forgot_password")
        response = self.client.post(forgot_url, {"email": "reset@nexova.ai"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Capture the reset token from mail
        reset_body = mail.outbox[-1].body
        otp_code = re.search(r"\b\d{6}\b", reset_body).group()

        # 2. Verify Reset OTP
        verify_url = reverse("auth_verify_reset_otp")
        response = self.client.post(verify_url, {"email": "reset@nexova.ai", "otp_code": otp_code}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # 3. Reset password
        reset_url = reverse("auth_reset_password")
        reset_data = {
            "email": "reset@nexova.ai",
            "otp_code": otp_code,
            "new_password": "NewSecurePassword123!",
            "confirm_new_password": "NewSecurePassword123!",
        }
        response = self.client.post(reset_url, reset_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Check password updated
        user.refresh_from_db()
        self.assertTrue(user.check_password("NewSecurePassword123!"))

    def test_change_password_flow(self):
        user = User.objects.create_user(
            username="changeuser",
            email="change@nexova.ai",
            password="OldSecurePassword123!"
        )
        self.client.force_authenticate(user=user)

        url = reverse("auth_change_password")
        data = {
            "old_password": "OldSecurePassword123!",
            "new_password": "NewSecurePassword123!",
            "confirm_new_password": "NewSecurePassword123!",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        user.refresh_from_db()
        self.assertTrue(user.check_password("NewSecurePassword123!"))

    def test_profile_retrieve_and_update(self):
        user = User.objects.create_user(
            username="profileuser",
            email="profile@nexova.ai",
            password="SecurePassword123!"
        )
        self.client.force_authenticate(user=user)

        # GET profile
        profile_url = reverse("auth_profile")
        response = self.client.get(profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["theme"], "light")

        # PATCH profile
        update_data = {
            "bio": "Expert Real Estate AI Specialist",
            "theme": "dark",
            "gender": "male",
            "location": "San Francisco",
        }
        response = self.client.patch(profile_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["theme"], "dark")
        self.assertEqual(response.data["data"]["bio"], "Expert Real Estate AI Specialist")

        # Verify DB records
        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.theme, "dark")
        self.assertEqual(profile.location, "San Francisco")
