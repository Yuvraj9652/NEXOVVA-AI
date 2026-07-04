from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.customers.serializers import CustomerSerializer, CustomerTimelineEventSerializer
from apps.customers.selectors import CustomerSelector
from apps.customers.services import CustomerService
from apps.authentication.permissions import IsOrganizationMember


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        return CustomerSelector.list_customers(
            organization=self.request.organization, search_query=search_query
        )

    def perform_create(self, serializer):
        customer = CustomerService.create_customer(
            organization=self.request.organization, **serializer.validated_data
        )
        serializer.instance = customer

    @action(detail=True, methods=["get", "post"])
    def timeline(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerTimelineEventSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            event = CustomerService.log_timeline_event(
                organization=request.organization,
                customer_id=customer.id,
                event_type=serializer.validated_data["event_type"],
                description=serializer.validated_data["description"],
            )
            return Response(
                CustomerTimelineEventSerializer(event).data, status=status.HTTP_201_CREATED
            )
        else:
            events = CustomerSelector.list_timeline_events(
                organization=request.organization, customer_id=customer.id
            )
            return Response(CustomerTimelineEventSerializer(events, many=True).data)
