from rest_framework import serializers
from apps.notes.models import Note
from apps.contacts.models import Contact
from apps.pipeline.models import Deal
from apps.leads.models import Lead
from apps.authentication.serializers import UserSerializer


class NoteSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source="author", read_only=True)

    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), required=False, allow_null=True
    )
    deal = serializers.PrimaryKeyRelatedField(
        queryset=Deal.objects.all(), required=False, allow_null=True
    )
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lead.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Note
        fields = [
            "id",
            "content",
            "author_details",
            "contact",
            "deal",
            "lead",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author_details", "created_at", "updated_at"]
