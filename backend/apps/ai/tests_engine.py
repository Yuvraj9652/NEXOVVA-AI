from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from apps.organizations.models import Organization
from apps.accounts.models import UserProfile
from apps.customers.models import Customer
from apps.ai.models import AICustomerChatSession, AICustomerChatMessage, AIChatMemory
from apps.broadcast.models import Campaign
from apps.properties.models import Project
from apps.tasks.models import Task
from apps.notes.models import Note

User = get_user_model()


class AIConversationEngineTests(APITestCase):
    def setUp(self):
        # Create Organizations
        self.org_a = Organization.objects.create(name="Org A", slug="org-a")
        self.org_b = Organization.objects.create(name="Org B", slug="org-b")

        # Create Users
        self.user_a = User.objects.create_user(username="usera", email="usera@org-a.com", password="Password123!")
        self.user_b = User.objects.create_user(username="userb", email="userb@org-b.com", password="Password123!")

        # UserProfiles
        UserProfile.objects.filter(user=self.user_a).update(organization=self.org_a, role=UserProfile.Roles.ADMIN)
        UserProfile.objects.filter(user=self.user_b).update(organization=self.org_b, role=UserProfile.Roles.ADMIN)

        # Create Projects
        self.proj_a = Project.objects.create(
            organization=self.org_a, name="Project A", city="City A", starting_price=100000.00
        )
        self.proj_b = Project.objects.create(
            organization=self.org_b, name="Project B", city="City B", starting_price=200000.00
        )

        # Create Customers
        self.cust_a = Customer.objects.create(
            organization=self.org_a, first_name="Cust", last_name="A", email="cust_a@example.com", phone="12345", customer_code="CUS-T00001"
        )
        self.cust_b = Customer.objects.create(
            organization=self.org_b, first_name="Cust", last_name="B", email="cust_b@example.com", phone="67890", customer_code="CUS-T00002"
        )

        # Create Campaigns
        self.camp_a = Campaign.objects.create(organization=self.org_a, name="Camp A", project=self.proj_a)
        self.camp_b = Campaign.objects.create(organization=self.org_b, name="Camp B", project=self.proj_b)

        # Create Sessions
        self.session_a = AICustomerChatSession.objects.create(
            organization=self.org_a, customer=self.cust_a, project=self.proj_a, campaign=self.camp_a, status="NEW"
        )

    @patch("apps.ai.ai_service.AIService._post")
    def test_intent_detection_greeting_skips_rag(self, mock_post):
        # Mock responses
        # 1. Intent Detection call: skips RAG
        # 2. Main structured response call
        mock_post.side_effect = [
            {"response": '{"need_rag": false, "intent": "GREETING"}'},
            {
                "response": (
                    '{"reply": "Hello! How can I help you?", "lead_stage": "NEW", '
                    '"budget_min": null, "budget_max": null, "preferred_location": null, '
                    '"buying_intent": "LOW", "needs_human": false}'
                )
            }
        ]

        url = reverse("ai_inbound_webhook")
        payload = {
            "sender_identity": "cust_a@example.com",
            "content": "Hi",
            "campaign_id": self.camp_a.id
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["reply"], "Hello! How can I help you?")
        self.assertFalse(response.data["needs_human"])

        # Check conversation session updated to active
        self.session_a.refresh_from_db()
        self.assertEqual(self.session_a.status, AICustomerChatSession.Statuses.WAITING_FOR_CUSTOMER)

        # Verify no CRM lead status update trigger occurred for greeting
        self.cust_a.refresh_from_db()
        self.assertEqual(self.cust_a.lead_status, Customer.LeadStatus.NEW)

    @patch("apps.ai.ai_service.AIService._post")
    def test_qualified_intent_updates_crm_and_generates_notes(self, mock_post):
        mock_post.side_effect = [
            {"response": '{"need_rag": true, "intent": "INFORMATION_REQUEST"}'},
            {
                "response": (
                    '{"reply": "Project A matches your 20M budget.", "lead_stage": "QUALIFIED", '
                    '"budget_min": 15000000, "budget_max": 25000000, "preferred_location": "Sector 62", '
                    '"buying_intent": "HIGH", "needs_human": true}'
                )
            }
        ]

        url = reverse("ai_inbound_webhook")
        payload = {
            "sender_identity": "cust_a@example.com",
            "content": "I am looking for a 3BHK with budget 20M in Sector 62.",
            "campaign_id": self.camp_a.id
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify CRM upgrades Customer status to VISITED/QUALIFIED
        self.cust_a.refresh_from_db()
        self.assertEqual(self.cust_a.lead_status, Customer.LeadStatus.VISITED)

        # Verify CRM note generated
        note = Note.objects.filter(customer=self.cust_a).first()
        self.assertIsNotNone(note)
        self.assertIn("HIGH", note.content)

        # Verify Task was generated for agent handoff
        task = Task.objects.filter(assigned_to=self.user_a).first()
        self.assertIsNotNone(task)
        self.assertEqual(task.title, "Follow-up request: Cust A")

        # Verify session status transitions to WAITING_FOR_AGENT
        self.session_a.refresh_from_db()
        self.assertEqual(self.session_a.status, AICustomerChatSession.Statuses.WAITING_FOR_AGENT)

        # Verify Chat Memory context details extracted
        memory = AIChatMemory.objects.get(session=self.session_a)
        self.assertEqual(memory.budget_min, 15000000.00)
        self.assertEqual(memory.preferred_location, "Sector 62")
        self.assertEqual(memory.buying_intent, "HIGH")

    @patch("apps.ai.ai_service.AIService._post")
    def test_waiting_for_agent_status_bypasses_ai(self, mock_post):
        # Set session to waiting for agent handoff
        self.session_a.status = AICustomerChatSession.Statuses.WAITING_FOR_AGENT
        self.session_a.save()

        url = reverse("ai_inbound_webhook")
        payload = {
            "sender_identity": "cust_a@example.com",
            "content": "Hello?",
        }

        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("sales representative has been notified", response.data["reply"])
        
        # Verify AI request was bypassed entirely (mock was not called)
        mock_post.assert_not_called()

    def test_tenant_scope_isolation(self):
        # Create a session under Org A trying to link to a customer under Org B
        with self.assertRaises(Exception):
            # Enforce that customer B cannot cross borders to Org A's session
            AICustomerChatSession.objects.create(
                organization=self.org_a,
                customer=self.cust_b,
                project=self.proj_a
            )

    def test_command_center_get_init(self):
        self.client.force_authenticate(user=self.user_a)
        url = reverse("ai_command_center")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check that it returns dynamic count metadata
        self.assertIn("1 customer records", response.data["reply"])
        self.assertIn("1 active properties", response.data["reply"])
        self.assertEqual(response.data["intent"], "SYSTEM_WELCOME")

    @patch("apps.ai.ai_service.AIService._post")
    def test_command_center_post_query(self, mock_post):
        mock_post.return_value = {
            "response": (
                '{"reply": "I recommend launching Palm Residency broadcast.", '
                '"intent": "RECOMMENDATION", "confidence": 95, "suggested_action": "LAUNCH_BROADCAST", '
                '"current_task": "Analyzing Campaigns", "current_crm_update": "None", '
                '"workspace_summary": "Palm Residency has high match potential.", "knowledge_source": "DB"}'
            )
        }
        self.client.force_authenticate(user=self.user_a)
        url = reverse("ai_command_center")
        payload = {"query": "Launch broadcast for Palm Residency"}
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["intent"], "RECOMMENDATION")
        self.assertEqual(response.data["suggested_action"], "LAUNCH_BROADCAST")

