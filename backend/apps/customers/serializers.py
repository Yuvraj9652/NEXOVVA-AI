from rest_framework import serializers
from apps.customers.models import (
    Customer,
    CustomerAddress,
    CustomerRequirement,
    CustomerSource,
    CustomerDocument,
    CustomerNote,
    CustomerActivity,
    CustomerCategory,
    CustomerList,
    CustomerListCustomer,
)


class CustomerAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAddress
        fields = "__all__"
        read_only_fields = ["id", "customer", "created_at", "updated_at"]


class CustomerRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerRequirement
        fields = "__all__"
        read_only_fields = ["id", "customer", "created_at", "updated_at"]


class CustomerSourceSerializer(serializers.ModelSerializer):
    added_by_employee = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerSource
        fields = "__all__"
        read_only_fields = ["id", "customer", "created_at", "updated_at"]


class CustomerDocumentSerializer(serializers.ModelSerializer):
    uploaded_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerDocument
        fields = "__all__"
        read_only_fields = ["id", "uploaded_at"]


class CustomerNoteSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerNote
        fields = "__all__"
        read_only_fields = ["id", "created_at"]


class CustomerActivitySerializer(serializers.ModelSerializer):
    performed_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerActivity
        fields = "__all__"
        read_only_fields = ["id", "timestamp"]


class CustomerCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerCategory
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class CustomerListCustomerSerializer(serializers.ModelSerializer):
    customer_data = serializers.SerializerMethodField()

    class Meta:
        model = CustomerListCustomer
        fields = ["id", "customer_list", "customer", "customer_data"]
        read_only_fields = ["id", "customer_list"]

    def get_customer_data(self, obj):
        return {
            "id": obj.customer.id,
            "customer_code": obj.customer.customer_code,
            "full_name": f"{obj.customer.first_name} {obj.customer.last_name}",
            "phone": obj.customer.phone,
            "email": obj.customer.email,
            "lead_status": obj.customer.lead_status,
            "source_type": obj.customer.source_type,
        }


class CustomerListSerializer(serializers.ModelSerializer):
    customers = CustomerListCustomerSerializer(many=True, read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CustomerList
        fields = ["id", "organization", "name", "description", "created_by", "created_at", "updated_at", "customer_count", "customers"]
        read_only_fields = ["id", "organization", "created_by", "created_at", "updated_at", "customer_count"]


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    address = CustomerAddressSerializer(read_only=True)
    requirements = CustomerRequirementSerializer(many=True, read_only=True)
    source_detail = CustomerSourceSerializer(read_only=True)
    documents = CustomerDocumentSerializer(many=True, read_only=True)
    notes = CustomerNoteSerializer(many=True, read_only=True)
    activities = CustomerActivitySerializer(many=True, read_only=True)
    assigned_employee = serializers.StringRelatedField(read_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id", "organization", "customer_code", "first_name", "last_name", "name",
            "email", "phone", "alternate_phone", "dob", "gender", "occupation",
            "company", "annual_income", "photo", "lead_status", "priority", "tags",
            "is_archived", "deleted_at", "assigned_employee", "created_by",
            "created_by_name", "source_type", "source_notes", "created_at", "updated_at",
            "address", "requirements", "source_detail", "documents", "notes", "activities",
        ]
        read_only_fields = ["id", "organization", "customer_code", "created_at", "updated_at"]

    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class CustomerBulkImportSerializer(serializers.Serializer):
    file = serializers.FileField(write_only=True)
    source_type = serializers.ChoiceField(choices=Customer.SourceType.choices, default=Customer.SourceType.CSV_IMPORT)
    added_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = ["file", "source_type", "added_by"]


class CustomerDuplicateCheckSerializer(serializers.Serializer):
    phone = serializers.CharField(required=False, allow_blank=True)
    email = serializers.CharField(required=False, allow_blank=True)
    name = serializers.CharField(required=False, allow_blank=True)
