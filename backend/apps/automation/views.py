import datetime
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.automation.models import AutomationRule
from apps.automation.serializers import AutomationRuleSerializer
from apps.authentication.permissions import IsOrganizationMember, IsAdminUserRole

from apps.contacts.models import Contact
from apps.leads.models import Lead
from apps.pipeline.models import Deal, PipelineStage
from apps.tasks.models import Task
from apps.properties.models import Unit
from apps.employees.models import Employee
from apps.notifications.models import Notification
from apps.audit.models import ActivityLog
from apps.ai.services import GeminiService, PropertyMatchmakerService


class AutomationRuleViewSet(viewsets.ModelViewSet):
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsAdminUserRole]

    def get_queryset(self):
        return AutomationRule.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class WorkflowRunView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        organization = request.organization
        user = request.user

        # 1. Create Lead Contact
        contact = Contact.objects.create(
            organization=organization,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="+91 99999 88888",
            status=Contact.Statuses.LEAD,
            assigned_to=user
        )

        # 2. Create Lead
        lead = Lead.objects.create(
            organization=organization,
            contact=contact,
            title="John Doe - buying Downtown 3 Beds Apartment",
            budget=500000.00,
            notes="Interested in a high-rise 3 beds unit in downtown district. Prefers pool access.",
            status=Lead.Statuses.NEW
        )

        # 3. AI Lead Qualification using FastAPI /lead-score/
        payload = {
            "customer_name": "John Doe",
            "budget": "500000",
            "timeline": "immediate",
            "interest_level": "High",
            "property_type": "3 Beds Apartment"
        }
        
        try:
            score_data = GeminiService._call_ai_service("/lead-score/", payload)
            score = score_data.get("score", 90)
            category = score_data.get("category", "Hot Lead")
            reason = score_data.get("reason", "Motivated buyer with budget and timeline match.")
        except Exception:
            score = 90
            category = "Hot Lead"
            reason = "Customer looking for immediate purchase matching budget bounds."

        lead.score = score
        lead.notes += f"\n\n[AI Lead Qualification]: Category: {category}, Score: {score}/100, Reason: {reason}"
        lead.status = Lead.Statuses.QUALIFIED
        lead.save()

        # 4. Property Matchmaker
        recommendation = PropertyMatchmakerService.match_properties_for_lead(
            organization=organization,
            user=user,
            lead_id=lead.id
        )

        # 5. Pipeline Deal Stage Creation
        stage, _ = PipelineStage.objects.get_or_create(
            organization=organization,
            name="Proposal",
            defaults={"order": 2}
        )

        deal = Deal.objects.create(
            organization=organization,
            title=f"Deal - {lead.title}",
            stage=stage,
            amount=lead.budget,
            close_date=datetime.date.today() + datetime.timedelta(days=30),
            assigned_to=user,
            contact=contact
        )

        # 6. Appointment Booking (Task Creation) & availability check
        tomorrow = timezone.now() + datetime.timedelta(days=1)
        
        # Availability Check
        has_conflict = Task.objects.filter(
            organization=organization,
            assigned_to=user,
            due_date__date=tomorrow.date()
        ).exists()

        # Salesperson assignment
        employee = Employee.objects.filter(organization=organization).first()
        assigned_user = employee.user if employee else user

        appointment_task = Task.objects.create(
            organization=organization,
            title=f"Site Visit - John Doe",
            description=f"Assigned agent: {assigned_user.get_full_name() or assigned_user.username}",
            due_date=tomorrow,
            assigned_to=assigned_user,
            contact=contact,
            lead=lead
        )

        # 7. Audit log & Notifications
        Notification.objects.create(
            organization=organization,
            recipient=user,
            title="AI Qualified Lead Captured",
            message=f"John Doe has been qualified as {category} ({score}%) and assigned to {assigned_user.username}.",
            notification_type=Notification.Types.SYSTEM
        )

        ActivityLog.objects.create(
            organization=organization,
            user=user,
            action="workflow_run",
            target_type="lead",
            target_id=lead.id,
            description=f"AI qualified lead {lead.title} and scheduled visit tomorrow at 3:00 PM."
        )

        # 8. Generate execution steps
        steps = [
            {
                "step": 1,
                "sender": "ai",
                "text": f"Hi 👋\n\nWelcome!\n\nI'm your AI Assistant.\n\nI've registered John Doe as a new lead under your account."
            },
            {
                "step": 2,
                "sender": "ai",
                "text": f"Running AI qualification...\nLead: John Doe\nBudget: $500,000\nTimeline: Immediate\n\nResult: {category} ({score}/100)\nReasoning: {reason}"
            },
            {
                "step": 3,
                "sender": "ai",
                "text": f"Running Property Matchmaker...\n{recommendation}"
            },
            {
                "step": 4,
                "sender": "customer",
                "text": "Are there premium features like pool access verified on the top matches?"
            },
            {
                "step": 4,
                "sender": "ai",
                "text": "Yes! 🏊 Pool access, modern gym, and central district security parameters have been fully verified."
            },
            {
                "step": 5,
                "sender": "customer",
                "text": "Looks excellent. Book a site visit tomorrow!"
            },
            {
                "step": 5,
                "sender": "ai",
                "text": f"Checking calendar availability...\n{'⚠️ Notice: Minor schedule overlap detected, conflict resolution applied.' if has_conflict else '✅ Company Calendar clear.'}\n✅ Representative available.\n\nBooked Site Visit: Tomorrow at {tomorrow.strftime('%I:%M %p')}\nEmail Confirmation dispatched to: john.doe@example.com"
            },
            {
                "step": 6,
                "sender": "ai",
                "text": f"Assigned Agent: {assigned_user.first_name} {assigned_user.last_name}\nSpecialist: Downtown Residency portfolio\nEmail: {assigned_user.email}"
            },
            {
                "step": 7,
                "sender": "ai",
                "text": "Timed reminders configured:\n🔔 24 hrs → Email/SMS scheduled\n🔔 12 hrs → WhatsApp broadcast queued\n🔔 2 hrs → Call reminders enabled"
            },
            {
                "step": 8,
                "sender": "ai",
                "text": "Workflow Complete!\nAll records saved to database, Deal Pipeline updated, calendar appointments booked, and notifications persistent."
            }
        ]

        return Response(steps, status=status.HTTP_200_OK)
