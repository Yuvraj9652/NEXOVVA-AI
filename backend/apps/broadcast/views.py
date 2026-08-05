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
from apps.properties.models import Project
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