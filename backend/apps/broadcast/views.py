from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.broadcast.models import (
    AudienceSegment,
    ContactList,
    BroadcastTemplate,
    Campaign,
    CampaignMessage,
    CampaignLog,
    CampaignAnalytics,
)
from apps.broadcast.serializers import (
    AudienceSegmentSerializer,
    ContactListSerializer,
    BroadcastTemplateSerializer,
    CampaignSerializer,
    CampaignMessageSerializer,
    CampaignLogSerializer,
    CampaignAnalyticsSerializer,
    CampaignSendSerializer,
    CampaignScheduleSerializer,
    CampaignImportSerializer,
    CampaignPreviewSerializer,
    AIAudienceMatchSerializer,
    AIContentGenerateSerializer,
    AIPersonalizeSerializer,
    AIScheduleOptimizerSerializer,
    AIDuplicateCheckSerializer,
    AIFollowUpSerializer,
)
from apps.broadcast.services import BroadcastService
from apps.broadcast.selectors import BroadcastSelector
from apps.broadcast.permissions import IsOrganizationMember, IsAdminOrManager
from django.core.mail import send_mail
from django.conf import settings
from apps.customers.models import Customer
import uuid


class AudienceSegmentViewSet(viewsets.ModelViewSet):
    serializer_class = AudienceSegmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return AudienceSegment.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class ContactListViewSet(viewsets.ModelViewSet):
    serializer_class = ContactListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return ContactList.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class BroadcastTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return BroadcastTemplate.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class CampaignViewSet(viewsets.ModelViewSet):
    serializer_class = CampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        queryset = Campaign.objects.filter(organization=self.request.organization)
        status = self.request.query_params.get("status")
        campaign_type = self.request.query_params.get("campaign_type")
        if status:
            queryset = queryset.filter(status=status)
        if campaign_type:
            queryset = queryset.filter(campaign_type=campaign_type)
        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        campaign_id = response.data.get("id")
        if campaign_id:
            campaign = Campaign.objects.get(id=campaign_id)
            if campaign.status == Campaign.Statuses.ACTIVE and campaign.target_type == "SELECTED_CUSTOMERS":
                summary = self.send_broadcast(campaign)
                response.data["broadcast_summary"] = summary
        return response

    def update(self, request, *args, **kwargs):
        campaign = self.get_object()
        old_status = campaign.status
        response = super().update(request, *args, **kwargs)
        campaign.refresh_from_db()
        if old_status != Campaign.Statuses.ACTIVE and campaign.status == Campaign.Statuses.ACTIVE and campaign.target_type == "SELECTED_CUSTOMERS":
            summary = self.send_broadcast(campaign)
            response.data["broadcast_summary"] = summary
        return response

    def send_broadcast(self, campaign):
        import logging
        logger = logging.getLogger(__name__)

        customer_ids = campaign.selected_customer_ids or []
        total_selected = len(customer_ids)

        if not customer_ids:
            return {
                "total_selected": 0,
                "successfully_sent": 0,
                "failed_count": 0,
                "failed_recipients": []
            }

        customers = Customer.objects.filter(id__in=customer_ids, organization=campaign.organization)
        found_ids = set(c.id for c in customers)

        successfully_sent = 0
        failed_count = 0
        failed_recipients = []

        # Handle non-existent customer IDs
        for cid in customer_ids:
            if cid not in found_ids:
                failed_count += 1
                failed_recipients.append({
                    "customer_id": cid,
                    "customer_name": f"Customer ID {cid}",
                    "email": "",
                    "reason": "Customer not found in database or does not belong to this organization"
                })

        project = campaign.project
        project_text = ""
        project_html = ""
        if project:
            project_text = f"\n\n--- Project Information ---\nProject: {project.name}\nBuilder: {project.builder}\nLocation: {project.city}\nProperty Type: {project.property_type}\nPrice Range: {project.starting_price} - {project.max_price}\nDescription: {project.short_description or project.description}"
            project_html = f"""
            <div style="margin-top: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
              <h3>Project Information: {project.name}</h3>
              <p><strong>Builder:</strong> {project.builder}</p>
              <p><strong>Location:</strong> {project.city}</p>
              <p><strong>Property Type:</strong> {project.property_type}</p>
              <p><strong>Price Range:</strong> {project.starting_price} - {project.max_price}</p>
              <p>{project.short_description or project.description}</p>
            </div>
            """

        image_html = ""
        image_text = ""
        if campaign.image_url:
            image_text = f"\n\nImage: {campaign.image_url}"
            image_html = f'<br/><br/><img src="{campaign.image_url}" alt="Campaign Image" style="max-width: 100%; height: auto;"/><br/><br/>'

        for customer in customers:
            email = customer.email
            if not email or "@" not in email:
                failed_count += 1
                failed_recipients.append({
                    "customer_id": customer.id,
                    "customer_name": f"{customer.first_name} {customer.last_name}",
                    "email": email or "",
                    "reason": "Missing or invalid email address"
                })
                # Log failed campaign message
                CampaignMessage.objects.create(
                    organization=campaign.organization,
                    campaign=campaign,
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    customer_phone=customer.phone,
                    customer_email=email or "",
                    channel="email",
                    message=campaign.content,
                    status=CampaignMessage.MessageStatus.FAILED,
                    failed_reason="Missing or invalid email address",
                )
                continue

            formatted_content = campaign.content.replace('\n', '<br/>')
            body_text = f"Hi {customer.first_name},\n\n{campaign.content}{image_text}{project_text}"
            body_html = f"""
            <html>
            <body>
              <p>Hi {customer.first_name},</p>
              <p>{formatted_content}</p>
              {image_html}
              {project_html}
            </body>
            </html>
            """

            try:
                send_mail(
                    subject=campaign.subject or campaign.name,
                    message=body_text,
                    from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@nexova.ai"),
                    recipient_list=[email],
                    html_message=body_html,
                    fail_silently=False
                )
                successfully_sent += 1
                # Log campaign message
                CampaignMessage.objects.create(
                    organization=campaign.organization,
                    campaign=campaign,
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    customer_phone=customer.phone,
                    customer_email=email,
                    channel="email",
                    message=campaign.content,
                    status=CampaignMessage.MessageStatus.SENT,
                )
            except Exception as e:
                logger.error(f"Failed to send email to {email}: {e}")
                failed_count += 1
                failed_recipients.append({
                    "customer_id": customer.id,
                    "customer_name": f"{customer.first_name} {customer.last_name}",
                    "email": email,
                    "reason": str(e)
                })
                # Log failed campaign message
                CampaignMessage.objects.create(
                    organization=campaign.organization,
                    campaign=campaign,
                    customer_name=f"{customer.first_name} {customer.last_name}",
                    customer_phone=customer.phone,
                    customer_email=email,
                    channel="email",
                    message=campaign.content,
                    status=CampaignMessage.MessageStatus.FAILED,
                    failed_reason=str(e),
                )

        summary = {
            "total_selected": total_selected,
            "successfully_sent": successfully_sent,
            "failed_count": failed_count,
            "failed_recipients": failed_recipients
        }

        # Update campaign total sent and reach
        campaign.total_sent = successfully_sent
        campaign.reach = str(successfully_sent)
        campaign.save(update_fields=["total_sent", "reach"])

        # Log completion
        BroadcastService.log_action(
            campaign,
            "BROADCAST",
            f"Email broadcast completed. Success: {successfully_sent}, Failed: {failed_count}."
        )

        return summary


    @action(detail=True, methods=["post"])
    def send(self, request, pk=None):
        campaign = self.get_object()
        data = request.data
        serializer = CampaignSendSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.send_campaign_message(campaign, serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def schedule(self, request, pk=None):
        campaign = self.get_object()
        data = request.data
        serializer = CampaignScheduleSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.schedule_campaign(campaign, serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def preview(self, request, pk=None):
        campaign = self.get_object()
        data = request.data
        serializer = CampaignPreviewSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.preview_campaign_message(campaign, serializer.validated_data)
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        campaign = self.get_object()
        duplicated = BroadcastService.duplicate_campaign(
            organization=self.request.organization, campaign=campaign, created_by=self.request.user
        )
        serializer = self.get_serializer(duplicated)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != Campaign.Statuses.RUNNING:
            return Response({"error": "Only running campaigns can be paused"}, status=status.HTTP_400_BAD_REQUEST)
        campaign.status = Campaign.Statuses.PAUSED
        campaign.save()
        BroadcastService.log_action(campaign, "PAUSE", f"Campaign paused by {self.request.user.username}")
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status != Campaign.Statuses.PAUSED:
            return Response({"error": "Only paused campaigns can be resumed"}, status=status.HTTP_400_BAD_REQUEST)
        campaign.status = Campaign.Statuses.ACTIVE
        campaign.save()
        BroadcastService.log_action(campaign, "RESUME", f"Campaign resumed by {self.request.user.username}")
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        campaign = self.get_object()
        if campaign.status not in [Campaign.Statuses.RUNNING, Campaign.Statuses.SCHEDULED, Campaign.Statuses.ACTIVE]:
            return Response({"error": "Only active/scheduled/running campaigns can be cancelled"}, status=status.HTTP_400_BAD_REQUEST)
        campaign.status = Campaign.Statuses.CANCELLED
        campaign.save()
        BroadcastService.log_action(campaign, "CANCEL", f"Campaign cancelled by {self.request.user.username}")
        serializer = self.get_serializer(campaign)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        organization = request.organization
        campaigns = Campaign.objects.filter(organization=organization)
        stats = {
            "total": campaigns.count(),
            "active": campaigns.filter(status=Campaign.Statuses.ACTIVE).count(),
            "running": campaigns.filter(status=Campaign.Statuses.RUNNING).count(),
            "scheduled": campaigns.filter(status=Campaign.Statuses.SCHEDULED).count(),
            "completed": campaigns.filter(status=Campaign.Statuses.COMPLETED).count(),
            "failed": campaigns.filter(status=Campaign.Statuses.FAILED).count(),
            "draft": campaigns.filter(status=Campaign.Statuses.DRAFT).count(),
            "paused": campaigns.filter(status=Campaign.Statuses.PAUSED).count(),
            "cancelled": campaigns.filter(status=Campaign.Statuses.CANCELLED).count(),
        }
        return Response(stats)

    @action(detail=False, methods=["post"])
    def import_csv(self, request):
        organization = request.organization
        serializer = CampaignImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.import_contacts(organization, serializer.validated_data)
        return Response(result, status=status.HTTP_201_CREATED)


class CampaignMessageViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CampaignMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        campaign_id = self.request.query_params.get("campaign_id")
        queryset = CampaignMessage.objects.filter(organization=self.request.organization)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset.order_by("-created_at")


class CampaignLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CampaignLogSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        campaign_id = self.request.query_params.get("campaign_id")
        queryset = CampaignLog.objects.filter(organization=self.request.organization)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        return queryset.order_by("-created_at")


class CampaignAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request, campaign_id=None):
        organization = request.organization
        if campaign_id:
            analytics = CampaignAnalytics.objects.filter(organization=organization, campaign_id=campaign_id).first()
            if not analytics:
                campaign = Campaign.objects.filter(organization=organization, id=campaign_id).first()
                if not campaign:
                    return Response({"error": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
                analytics = CampaignAnalytics.objects.create(organization=organization, campaign=campaign)
            serializer = CampaignAnalyticsSerializer(analytics)
            return Response(serializer.data)

        analytics_qs = CampaignAnalytics.objects.filter(organization=organization)
        serializer = CampaignAnalyticsSerializer(analytics_qs, many=True)
        return Response(serializer.data)


class AIAudienceMatchView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIAudienceMatchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_audience_match(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            query=serializer.validated_data["query"],
            filters=serializer.validated_data.get("filters", {}),
        )
        return Response(result, status=status.HTTP_200_OK)


class AIContentGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIContentGenerateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_generate_content(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            content_type=serializer.validated_data["content_type"],
            audience_segment=serializer.validated_data.get("audience_segment", ""),
        )
        return Response(result, status=status.HTTP_200_OK)


class AIPersonalizeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIPersonalizeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_personalize_message(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            customer_name=serializer.validated_data["customer_name"],
            customer_phone=serializer.validated_data.get("customer_phone", ""),
            customer_email=serializer.validated_data.get("customer_email", ""),
            content_type=serializer.validated_data["content_type"],
        )
        return Response(result, status=status.HTTP_200_OK)


class AIScheduleOptimizerView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIScheduleOptimizerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_optimize_schedule(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            audience_size=serializer.validated_data.get("audience_size", 100),
        )
        return Response(result, status=status.HTTP_200_OK)


class AIDuplicateCheckView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIDuplicateCheckSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_check_duplicate(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            customer_phone=serializer.validated_data["customer_phone"],
            customer_email=serializer.validated_data.get("customer_email", ""),
        )
        return Response(result, status=status.HTTP_200_OK)


class AIFollowUpView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        serializer = AIFollowUpSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = BroadcastService.ai_follow_up(
            organization=request.organization,
            campaign_id=serializer.validated_data["campaign_id"],
            customer_id=serializer.validated_data["customer_id"],
            message_status=serializer.validated_data["message_status"],
            days_since_sent=serializer.validated_data.get("days_since_sent", 0),
        )
        return Response(result, status=status.HTTP_200_OK)