from rest_framework import serializers
from apps.documents.models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "file", "extracted_text", "version", "created_at", "updated_at"]
        read_only_fields = ["id", "extracted_text", "version", "created_at", "updated_at"]
