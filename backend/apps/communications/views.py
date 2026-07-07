from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.authentication.permissions import IsOrganizationMember
from .services import CommunicationService


class CommunicationView(APIView):
    permission_classes = [IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        return Response(
            CommunicationService.get_summary(request.organization)
        )