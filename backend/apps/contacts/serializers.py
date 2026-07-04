from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.contacts.models import Contact
from apps.authentication.serializers import UserSerializer

User = get_user_model()


class ContactSerializer(serializers.ModelSerializer):
    assigned_to_details = UserSerializer(source="assigned_to", read_only=True)
    assigned_to = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Contact
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "status",
            "assigned_to",
            "assigned_to_details",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
