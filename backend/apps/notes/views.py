from rest_framework import viewsets, permissions, exceptions
from apps.notes.serializers import NoteSerializer
from apps.notes.selectors import NotesSelector
from apps.notes.services import NotesService
from apps.authentication.permissions import IsOrganizationMember
from apps.accounts.models import UserProfile


class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        contact_id = self.request.query_params.get("contact")
        deal_id = self.request.query_params.get("deal")
        lead_id = self.request.query_params.get("lead")

        return NotesSelector.list_notes(
            organization=self.request.organization,
            contact_id=contact_id,
            deal_id=deal_id,
            lead_id=lead_id,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        contact = validated_data.pop("contact", None)
        deal = validated_data.pop("deal", None)
        lead = validated_data.pop("lead", None)

        note = NotesService.create_note(
            organization=self.request.organization,
            author=self.request.user,
            contact_id=contact.id if contact else None,
            deal_id=deal.id if deal else None,
            lead_id=lead.id if lead else None,
            **validated_data,
        )
        serializer.instance = note

    def perform_update(self, serializer):
        # Restrict modification to note author or org admin
        instance = self.get_object()
        if (
            instance.author != self.request.user
            and self.request.user.userprofile.role != UserProfile.Roles.ADMIN
        ):
            raise exceptions.PermissionDenied("You do not have permission to edit this note.")

        note = NotesService.update_note(
            organization=self.request.organization,
            author=self.request.user,
            note_id=instance.id,
            content=serializer.validated_data.get("content"),
        )
        serializer.instance = note

    def perform_destroy(self, instance):
        if (
            instance.author != self.request.user
            and self.request.user.userprofile.role != UserProfile.Roles.ADMIN
        ):
            raise exceptions.PermissionDenied("You do not have permission to delete this note.")

        NotesService.delete_note(
            organization=self.request.organization,
            author=self.request.user,
            note_id=instance.id,
        )
