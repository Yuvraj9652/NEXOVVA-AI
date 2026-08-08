import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.customers.models import Customer
from apps.customers.services import CustomerService
from apps.ai.models import AICustomerChatSession
from apps.ai.conversation_engine import ConversationEngine
from apps.broadcast.models import Campaign
from apps.properties.models import Project

logger = logging.getLogger("ai_service")


class InboundWebhookView(APIView):
    permission_classes = [AllowAny]  # Public webhook endpoint simulating channel integrations

    def post(self, request):
        sender_identity = request.data.get("sender_identity")
        content = request.data.get("content")
        channel_type = request.data.get("channel_type", "EMAIL")
        campaign_id = request.data.get("campaign_id")
        project_id = request.data.get("project_id")

        if not sender_identity or not content:
            return Response(
                {"error": "sender_identity and content are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        sender_identity = sender_identity.strip()
        content = content.strip()

        # 1. Resolve Customer and Tenant (Organization) Context
        customer = Customer.objects.filter(email__iexact=sender_identity).first()
        if not customer:
            customer = Customer.objects.filter(phone=sender_identity).first()

        if customer:
            org = customer.organization
        else:
            # Fallback to the first organization or create a Default organization
            from apps.organizations.models import Organization
            org = Organization.objects.first()
            if not org:
                org, _ = Organization.objects.get_or_create(name="Default Organization")
            
            # Auto-create customer
            customer, _ = CustomerService.get_or_create_customer(
                organization=org,
                identity=sender_identity,
                default_fields={
                    "first_name": "Inbound",
                    "last_name": "Lead",
                    "lead_status": Customer.LeadStatus.NEW
                }
            )

        # 2. Resolve Campaign and Project link
        campaign = None
        project = None
        if campaign_id:
            campaign = Campaign.objects.filter(organization=org, id=campaign_id).first()
            if campaign and campaign.project:
                project = campaign.project
        if project_id and not project:
            project = Project.objects.filter(organization=org, id=project_id).first()

        # 3. Fetch/Create Session
        # Get active session for customer or start a new one
        session = AICustomerChatSession.objects.filter(
            organization=org,
            customer=customer,
            status__in=[
                AICustomerChatSession.Statuses.NEW,
                AICustomerChatSession.Statuses.ACTIVE,
                AICustomerChatSession.Statuses.WAITING_FOR_CUSTOMER,
                AICustomerChatSession.Statuses.WAITING_FOR_AI,
                AICustomerChatSession.Statuses.WAITING_FOR_AGENT
            ]
        ).first()

        if not session:
            session = AICustomerChatSession.objects.create(
                organization=org,
                customer=customer,
                project=project,
                campaign=campaign,
                status=AICustomerChatSession.Statuses.NEW
            )
            logger.info(f"Initialized new inbound chat session {session.id} for customer {customer.email or customer.phone}")
        else:
            # Update project/campaign links if not already set
            if project and not session.project:
                session.project = project
            if campaign and not session.campaign:
                session.campaign = campaign
            session.save()

        # 4. Process Message via ConversationEngine
        try:
            result = ConversationEngine.process_message(session, content)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"InboundWebhookView processing failed: {e}", exc_info=True)
            return Response(
                {"error": f"Failed to process message: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
