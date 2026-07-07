from rest_framework.views import APIView
from rest_framework.response import Response


class BillingView(APIView):
    def get(self, request):
        return Response({"message": "Billing module coming soon"})