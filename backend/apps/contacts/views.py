from rest_framework import viewsets, permissions
from apps.contacts.serializers import ContactSerializer
from apps.contacts.selectors import ContactSelector
from apps.contacts.services import ContactService
from apps.authentication.permissions import IsOrganizationMember


class ContactViewSet(viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        status_filter = self.request.query_params.get("status")
        return ContactSelector.list_contacts(
            organization=self.request.organization,
            search_query=search_query,
            status=status_filter,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        # Resolve assigned_to
        assigned_to = validated_data.pop("assigned_to", None)
        assigned_to_id = assigned_to.id if assigned_to else None

        contact = ContactService.create_contact(
            organization=self.request.organization,
            user=self.request.user,
            assigned_to_id=assigned_to_id,
            **validated_data,
        )
        serializer.instance = contact

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        # Resolve assigned_to
        assigned_to_id = None
        if "assigned_to" in validated_data:
            assigned_to = validated_data.pop("assigned_to")
            assigned_to_id = assigned_to.id if assigned_to else None
        elif self.get_object().assigned_to:
            assigned_to_id = self.get_object().assigned_to.id

        contact = ContactService.update_contact(
            organization=self.request.organization,
            user=self.request.user,
            contact_id=self.get_object().id,
            assigned_to_id=assigned_to_id,
            **validated_data,
        )
        serializer.instance = contact

    def perform_destroy(self, instance):
        ContactService.delete_contact(
            organization=self.request.organization,
            user=self.request.user,
            contact_id=instance.id,
        )
