from rest_framework.views import APIView
from rest_framework.response import Response


class SubscriptionView(APIView):
    def get(self, request):
        return Response({"message": "Subscriptions module coming soon"})