from rest_framework import serializers
from apps.customers.models import Customer, CustomerTimelineEvent


class CustomerTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTimelineEvent
        fields = ["id", "customer", "event_type", "description", "created_at"]
        read_only_fields = ["id", "created_at"]


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ["id", "first_name", "last_name", "email", "phone", "segment", "created_at"]
        read_only_fields = ["id", "created_at"]
