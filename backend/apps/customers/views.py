from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
import csv
import json
from datetime import datetime

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
from apps.customers.serializers import (
    CustomerSerializer,
    CustomerAddressSerializer,
    CustomerRequirementSerializer,
    CustomerSourceSerializer,
    CustomerDocumentSerializer,
    CustomerNoteSerializer,
    CustomerActivitySerializer,
    CustomerCategorySerializer,
    CustomerListSerializer,
    CustomerListCustomerSerializer,
    CustomerBulkImportSerializer,
    CustomerDuplicateCheckSerializer,
)
from apps.customers.selectors import CustomerSelector
from apps.customers.services import CustomerService
from apps.authentication.permissions import IsOrganizationMember, IsManagerUserRole


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        search = self.request.query_params.get("search")
        lead_status = self.request.query_params.get("lead_status")
        source_type = self.request.query_params.get("source_type")
        city = self.request.query_params.get("city")
        assigned_employee = self.request.query_params.get("assigned_employee")
        priority = self.request.query_params.get("priority")
        tags = self.request.query_params.get("tags")
        created_after = self.request.query_params.get("created_after")
        created_before = self.request.query_params.get("created_before")
        is_archived = self.request.query_params.get("archived", "false").lower() == "true"

        return CustomerSelector.list_customers(
            organization=self.request.organization,
            search_query=search,
            lead_status=lead_status,
            source_type=source_type,
            city=city,
            assigned_employee=assigned_employee,
            priority=priority,
            tags=tags,
            created_after=created_after,
            created_before=created_before,
            is_archived=is_archived,
        )

    def create(self, request, *args, **kwargs):
        city = request.data.get("city", "")
        property_type = request.data.get("property_type", "")
        budget_min = request.data.get("budget_min")
        budget_max = request.data.get("budget_max")
        purpose = request.data.get("purpose", "")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save(
            organization=request.organization,
            created_by=request.user,
        )

        if city:
            CustomerAddress.objects.update_or_create(
                customer=customer,
                defaults={"organization": request.organization, "city": city, "country": "India"}
            )

        if property_type or budget_min or budget_max or purpose:
            try:
                b_min = float(budget_min) if budget_min not in [None, ""] else None
            except (ValueError, TypeError):
                b_min = None

            try:
                b_max = float(budget_max) if budget_max not in [None, ""] else None
            except (ValueError, TypeError):
                b_max = None

            CustomerRequirement.objects.update_or_create(
                customer=customer,
                defaults={
                    "organization": request.organization,
                    "property_type": property_type,
                    "budget_min": b_min,
                    "budget_max": b_max,
                    "purpose": purpose,
                    "preferred_city": city,
                }
            )

        headers = self.get_success_headers(serializer.data)
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        customer = self.get_object()
        city = request.data.get("city")
        property_type = request.data.get("property_type")
        budget_min = request.data.get("budget_min")
        budget_max = request.data.get("budget_max")
        purpose = request.data.get("purpose")

        serializer = self.get_serializer(customer, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        customer = serializer.save()

        if city is not None:
            CustomerAddress.objects.update_or_create(
                customer=customer,
                defaults={"organization": request.organization, "city": city, "country": "India"}
            )

        if any(v is not None for v in [property_type, budget_min, budget_max, purpose]):
            try:
                b_min = float(budget_min) if budget_min not in [None, ""] else None
            except (ValueError, TypeError):
                b_min = None

            try:
                b_max = float(budget_max) if budget_max not in [None, ""] else None
            except (ValueError, TypeError):
                b_max = None

            req = customer.requirements.first()
            if req:
                if property_type is not None: req.property_type = property_type
                if b_min is not None: req.budget_min = b_min
                if b_max is not None: req.budget_max = b_max
                if purpose is not None: req.purpose = purpose
                if city is not None: req.preferred_city = city
                req.save()
            else:
                CustomerRequirement.objects.create(
                    organization=request.organization,
                    customer=customer,
                    property_type=property_type or "",
                    budget_min=b_min,
                    budget_max=b_max,
                    purpose=purpose or "",
                    preferred_city=city or "",
                )

        return Response(CustomerSerializer(customer).data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        stats = CustomerSelector.get_stats(request.organization)
        return Response(stats)

    @action(detail=False, methods=["get"])
    def trash(self, request):
        customers = CustomerSelector.list_customers(
            organization=request.organization,
            is_archived=True,
        )
        return Response(CustomerSerializer(customers, many=True).data)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        customer = self.get_object()
        CustomerService.archive_customer(
            organization=request.organization,
            customer_id=customer.id,
            archived_by=request.user,
        )
        return Response({"status": "archived"})

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        customer = self.get_object()
        CustomerService.restore_customer(
            organization=request.organization,
            customer_id=customer.id,
            restored_by=request.user,
        )
        return Response({"status": "restored"})

    @action(detail=True, methods=["delete"])
    def delete_permanently(self, request, pk=None):
        customer = self.get_object()
        customer.delete()
        return Response({"status": "deleted"})

    @action(detail=True, methods=["get", "post"])
    def address(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerAddressSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organization=request.organization, customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        address = getattr(customer, "address", None)
        if address:
            return Response(CustomerAddressSerializer(address).data)
        return Response({})

    @action(detail=True, methods=["get", "post"])
    def requirements(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerRequirementSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organization=request.organization, customer=customer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(CustomerRequirementSerializer(customer.requirements.all(), many=True).data)

    @action(detail=True, methods=["get", "post"])
    def source(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerSourceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organization=request.organization, customer=customer, added_by_employee=getattr(request.user, "employee_profile", None))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        source = getattr(customer, "source_detail", None)
        if source:
            return Response(CustomerSourceSerializer(source).data)
        return Response({})

    @action(detail=True, methods=["get", "post"])
    def documents(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerDocumentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organization=request.organization, customer=customer, uploaded_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(CustomerDocumentSerializer(customer.documents.all(), many=True).data)

    @action(detail=True, methods=["get", "post"])
    def notes(self, request, pk=None):
        customer = self.get_object()
        if request.method == "POST":
            serializer = CustomerNoteSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(organization=request.organization, customer=customer, created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(CustomerNoteSerializer(customer.notes.all(), many=True).data)

    @action(detail=True, methods=["get"])
    def timeline(self, request, pk=None):
        customer = self.get_object()
        timeline = CustomerSelector.get_timeline(
            organization=request.organization,
            customer_id=customer.id,
        )
        return Response(timeline)

    @action(detail=False, methods=["post"])
    def check_duplicates(self, request):
        serializer = CustomerDuplicateCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        duplicates = CustomerSelector.find_duplicates(
            organization=request.organization,
            phone=serializer.validated_data.get("phone", ""),
            email=serializer.validated_data.get("email", ""),
            name=serializer.validated_data.get("name", ""),
        )
        return Response({"duplicates": duplicates})

    @action(detail=False, methods=["post"])
    def bulk_import(self, request):
        serializer = CustomerBulkImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        file = serializer.validated_data["file"]
        source_type = serializer.validated_data.get("source_type", Customer.SourceType.CSV_IMPORT)

        content = file.read().decode("utf-8")
        rows = CustomerService.parse_csv(content)

        result = CustomerService.bulk_import(
            organization=request.organization,
            parsed_rows=rows,
            source_type=source_type,
            imported_by=request.user,
        )
        return Response({
            "total_records": len(rows),
            "created": result["created"],
            "duplicates": result["duplicates"],
            "invalid": result["invalid"],
            "errors": result["errors"],
        })

    @action(detail=False, methods=["get"])
    def export(self, request):
        customers = CustomerSelector.list_customers(organization=request.organization)
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="customers_export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            "customer_code", "first_name", "last_name", "email", "phone",
            "alternate_phone", "lead_status", "priority", "source_type",
            "company", "city", "budget_min", "budget_max", "created_at",
        ])
        for c in customers:
            writer.writerow([
                c.customer_code, c.first_name, c.last_name, c.email, c.phone,
                c.alternate_phone, c.lead_status, c.priority, c.source_type,
                c.company, c.address.city if hasattr(c, "address") else "",
                c.requirements.first().budget_min if c.requirements.exists() else "",
                c.requirements.first().budget_max if c.requirements.exists() else "",
                c.created_at,
            ])
        return response


class CustomerAddressViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerAddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerAddress.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class CustomerRequirementViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerRequirementSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerRequirement.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class CustomerSourceViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSourceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerSource.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class CustomerDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return CustomerDocument.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, uploaded_by=self.request.user)


class CustomerNoteViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerNoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerNote.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class CustomerActivityViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CustomerActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerActivity.objects.filter(organization=self.request.organization)


class CustomerCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerCategory.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)


class CustomerListViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerListSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return CustomerList.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def add_customers(self, request, pk=None):
        customer_list = self.get_object()
        customer_ids = request.data.get("customer_ids", [])
        added = CustomerService.add_to_list(
            organization=request.organization,
            list_id=customer_list.id,
            customer_ids=customer_ids,
        )
        return Response({"added": added})

    @action(detail=True, methods=["post"])
    def remove_customers(self, request, pk=None):
        customer_list = self.get_object()
        customer_ids = request.data.get("customer_ids", [])
        removed = CustomerService.remove_from_list(
            organization=request.organization,
            list_id=customer_list.id,
            customer_ids=customer_ids,
        )
        return Response({"removed": removed})

    @action(detail=True, methods=["get"])
    def customers(self, request, pk=None):
        customer_list = self.get_object()
        list_customers = CustomerSelector.get_list_customers(
            organization=request.organization,
            list_id=customer_list.id,
        )
        return Response(CustomerListCustomerSerializer(list_customers, many=True).data)
