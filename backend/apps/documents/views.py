from rest_framework import viewsets, permissions
from apps.documents.serializers import DocumentSerializer
from apps.documents.selectors import DocumentSelector
from apps.documents.services import DocumentService
from apps.authentication.permissions import IsOrganizationMember


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return DocumentSelector.list_documents(organization=self.request.organization)

    def perform_create(self, serializer):
        doc = DocumentService.upload_document(
            organization=self.request.organization,
            name=serializer.validated_data["name"],
            file=serializer.validated_data["file"],
        )
        serializer.instance = doc
