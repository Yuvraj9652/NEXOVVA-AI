from rest_framework import serializers
from apps.leads.models import Lead
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.contacts.serializers import ContactSerializer
from apps.companies.serializers import CompanySerializer


class LeadSerializer(serializers.ModelSerializer):
    contact_details = ContactSerializer(source="contact", read_only=True)
    company_details = CompanySerializer(source="company", read_only=True)

    contact = serializers.PrimaryKeyRelatedField(
        queryset=Contact.objects.all(), required=False, allow_null=True
    )
    company = serializers.PrimaryKeyRelatedField(
        queryset=Company.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Lead
        fields = [
            "id",
            "title",
            "contact",
            "contact_details",
            "company",
            "company_details",
            "status",
            "source",
            "budget",
            "notes",
            "score",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
