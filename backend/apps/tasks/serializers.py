from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.tasks.models import Task
from apps.contacts.models import Contact
from apps.pipeline.models import Deal
from apps.leads.models import Lead
from apps.contacts.serializers import ContactSerializer
from apps.pipeline.serializers import DealSerializer
from apps.leads.serializers import LeadSerializer
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class TasksSerializer(serializers.ModelSerializer):
    assigned_to_details = UserSerializer(source="assigned_to", read_only=True)
    contact_details = ContactSerializer(source="contact", read_only=True)
    deal_details = DealSerializer(source="deal", read_only=True)
    lead_details = LeadSerializer(source="lead", read_only=True)

    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
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
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "due_date",
            "completed",
            "assigned_to",
            "assigned_to_details",
            "contact",
            "contact_details",
            "deal",
            "deal_details",
            "lead",
            "lead_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
