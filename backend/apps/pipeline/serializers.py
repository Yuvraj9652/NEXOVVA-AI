from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.pipeline.models import PipelineStage, Deal
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.contacts.serializers import ContactSerializer
from apps.companies.serializers import CompanySerializer
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class PipelineStageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PipelineStage
        fields = ["id", "name", "order", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class DealSerializer(serializers.ModelSerializer):
    stage_details = PipelineStageSerializer(source="stage", read_only=True)
    assigned_to_details = UserSerializer(source="assigned_to", read_only=True)
    contact_details = ContactSerializer(source="contact", read_only=True)
    company_details = CompanySerializer(source="company", read_only=True)

    stage = serializers.PrimaryKeyRelatedField(queryset=PipelineStage.objects.all())
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )
    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), required=False, allow_null=True
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Deal
        fields = [
            "id",
            "title",
            "stage",
            "stage_details",
            "amount",
            "close_date",
            "assigned_to",
            "assigned_to_details",
            "contact",
            "contact_details",
            "company",
            "company_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
