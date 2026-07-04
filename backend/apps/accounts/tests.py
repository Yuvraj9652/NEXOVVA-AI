from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from apps.accounts.models import UserProfile
from apps.organizations.models import Organization

User = get_user_model()


class AuthenticationIntegrationTests(APITestCase):
    def test_user_registration_creates_organization_and_profile(self):
        url = reverse("auth_register")
        data = {
            "username": "testagent",
            "email": "testagent@nexova.ai",
            "password": "SecurePassword123!",
            "first_name": "Test",
            "last_name": "Agent",
            "organization_name": "Nexova Realty",
        }

        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("profile", response.data)
        self.assertEqual(response.data["profile"]["role"], UserProfile.Roles.ADMIN)
        self.assertEqual(response.data["profile"]["organization"]["name"], "Nexova Realty")

        # Verify DB records
        user = User.objects.get(username="testagent")
        self.assertEqual(user.email, "testagent@nexova.ai")
        
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.role, UserProfile.Roles.ADMIN)
        self.assertEqual(profile.organization.name, "Nexova Realty")

    def test_user_login_returns_token_and_user_details(self):
        # First register
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

        # Now login
        login_url = reverse("auth_login")
        login_data = {
            "username": "testagent",
            "password": "SecurePassword123!",
        }

        response = self.client.post(login_url, login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["username"], "testagent")
        self.assertEqual(response.data["user"]["role"], UserProfile.Roles.ADMIN)
        self.assertEqual(response.data["user"]["organization"]["name"], "Nexova Realty")
