from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.authentication.permissions import IsOrganizationMember
from .models import BroadcastCampaign
from .serializers import BroadcastCampaignSerializer
from .services import CommunicationService


class CommunicationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        return Response(
            CommunicationService.get_summary(request.organization)
        )


class BroadcastCampaignViewSet(viewsets.ModelViewSet):
    serializer_class = BroadcastCampaignSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return BroadcastCampaign.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        import random
        reach = f"{random.randint(1, 9)}.{random.randint(0, 9)}K"
        
        name = serializer.validated_data.get("name", "")
        # Call AI service to generate campaign copy based on the campaign name
        from apps.ai.ai_service import AIService
        try:
            prompt = (
                f"You are a real estate digital marketing specialist.\n"
                f"Create a catchy, highly engaging, and professional real estate broadcast campaign message copy "
                f"for a campaign named: '{name}'. Make it under 3 sentences."
            )
            ai_message = AIService.call_chat(session_id="campaign_generation", message=prompt)
        except Exception:
            ai_message = f"Exciting news! We are launching our new campaign: '{name}'. Contact our agents today to learn more!"

        serializer.save(organization=self.request.organization, reach=reach, content=ai_message)