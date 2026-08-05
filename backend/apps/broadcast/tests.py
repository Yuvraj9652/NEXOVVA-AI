from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.organizations.models import Organization
from apps.accounts.models import UserProfile
from apps.customers.models import Customer
from apps.broadcast.models import Campaign, CampaignMessage
from apps.properties.models import Project

User = get_user_model()


class EmailBroadcastTests(APITestCase):
    def setUp(self):
        # Create organization
        self.org = Organization.objects.create(name="Acme Grop", slug="acme-grop")

        # Create user
        self.user = User.objects.create_user(
            username="acmeadmin",
            email="admin@acmegrop.com",
            password="Password123!"
        )

        # Setup UserProfile for the organization
        self.user_profile = UserProfile.objects.get(user=self.user)
        self.user_profile.organization = self.org
        self.user_profile.role = UserProfile.Roles.ADMIN
        self.user_profile.save()

        # Create project
        self.project = Project.objects.create(
            organization=self.org,
            name="DLF Cyber Horizon",
            builder="DLF Homes",
            city="Gurugram",
            property_type=Project.PropertyType.APARTMENT,
            starting_price=15000000.00,
            max_price=32000000.00,
            description="Ultra luxury apartments"
        )

        # Create customers
        self.cust_valid = Customer.objects.create(
            organization=self.org,
            first_name="Sarinah",
            last_name="Shah",
            email="sarinah.shah@example.com",
            phone="8980133121"
        )

        self.cust_invalid_email = Customer.objects.create(
            organization=self.org,
            first_name="Yuvraj",
            last_name="Labana",
            email="invalidemail", # Missing @ symbol
            phone="7878596585"
        )

        self.cust_no_email = Customer.objects.create(
            organization=self.org,
            first_name="Neel",
            last_name="Patel",
            email="", # Empty email
            phone="8734071590"
        )

        # Create campaign (Draft)
        self.campaign = Campaign.objects.create(
            organization=self.org,
            name="Launch Showcase",
            subject="Exclusive VIP Preview",
            campaign_type=Campaign.CampaignType.PROJECT_LAUNCH,
            project=self.project,
            status=Campaign.Statuses.DRAFT,
            target_type="SELECTED_CUSTOMERS",
            selected_customer_ids=[self.cust_valid.id, self.cust_invalid_email.id, self.cust_no_email.id, 99999], # 99999 is non-existent
            content="Welcome to our new launch event!",
            created_by=self.user
        )

        self.client.force_authenticate(user=self.user)

    def test_campaign_broadcast_sends_emails_correctly(self):
        mail.outbox = []

        url = reverse("campaign-detail", kwargs={"pk": self.campaign.id})
        payload = {
            "status": "Active",
            "total_sent": 3,
            "reach": "3"
        }

        response = self.client.patch(url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify broadcast summary in response
        self.assertIn("broadcast_summary", response.data)
        summary = response.data["broadcast_summary"]
        self.assertEqual(summary["total_selected"], 4)
        self.assertEqual(summary["successfully_sent"], 1) # Only cust_valid is sent successfully
        self.assertEqual(summary["failed_count"], 3) # cust_invalid_email, cust_no_email, 99999 are failed
        
        # Verify mail outbox has 1 email
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["sarinah.shah@example.com"])
        self.assertEqual(mail.outbox[0].subject, "Exclusive VIP Preview")
        self.assertIn("Hi Sarinah", mail.outbox[0].body)
        self.assertIn("DLF Cyber Horizon", mail.outbox[0].body)
        
        # Verify campaign messages logged in database
        sent_messages = CampaignMessage.objects.filter(campaign=self.campaign, status=CampaignMessage.MessageStatus.SENT)
        self.assertEqual(sent_messages.count(), 1)
        self.assertEqual(sent_messages.first().customer_email, "sarinah.shah@example.com")
        
        failed_messages = CampaignMessage.objects.filter(campaign=self.campaign, status=CampaignMessage.MessageStatus.FAILED)
        # Only the database-existent but failed email attempts are logged in CampaignMessage
        # Non-existent customer 99999 doesn't create CampaignMessage database record
        self.assertEqual(failed_messages.count(), 2) 
