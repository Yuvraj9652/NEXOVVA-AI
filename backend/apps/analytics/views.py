from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsOrganizationMember
from .services import AnalyticsService


class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        data = AnalyticsService.get_analytics(request.organization)
        return Response(data)