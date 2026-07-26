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
        serializer.save(organization=self.request.organization, reach=reach)