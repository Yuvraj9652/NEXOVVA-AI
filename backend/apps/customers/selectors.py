from django.db.models import Q, Max
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


class CustomerSelector:
    @staticmethod
    def list_customers(
        organization,
        search_query=None,
        lead_status=None,
        source_type=None,
        city=None,
        assigned_employee=None,
        priority=None,
        tags=None,
        created_after=None,
        created_before=None,
        is_archived=False,
    ):
        queryset = Customer.objects.filter(organization=organization)

        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
                | Q(phone__icontains=search_query)
                | Q(alternate_phone__icontains=search_query)
                | Q(company__icontains=search_query)
                | Q(customer_code__icontains=search_query)
            )

        if lead_status:
            queryset = queryset.filter(lead_status=lead_status)

        if source_type:
            queryset = queryset.filter(source_type=source_type)

        if city:
            queryset = queryset.filter(address__city__icontains=city)

        if assigned_employee:
            queryset = queryset.filter(assigned_employee_id=assigned_employee)

        if priority:
            queryset = queryset.filter(priority=priority)

        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            for tag in tag_list:
                queryset = queryset.filter(tags__contains=[tag])

        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)

        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)

        if is_archived:
            queryset = queryset.filter(is_archived=True)
        else:
            queryset = queryset.filter(is_archived=False)

        return queryset.distinct()

    @staticmethod
    def get_customer(organization, customer_id):
        return Customer.objects.filter(organization=organization, id=customer_id).first()

    @staticmethod
    def get_stats(organization):
        base = Customer.objects.filter(organization=organization)
        total = base.count()
        active = base.filter(deleted_at__isnull=True).count()
        archived = base.filter(is_archived=True).count()
        new_this_month = base.filter(
            created_at__month=1,
            created_at__year=2026,
        ).count()
        return {
            "total_customers": total,
            "active_customers": active,
            "imported_customers": base.filter(source_type=Customer.SourceType.CSV_IMPORT).count(),
            "manual_entries": base.exclude(source_type=Customer.SourceType.CSV_IMPORT).count(),
            "hot_leads": base.filter(lead_status=Customer.LeadStatus.HOT).count(),
            "cold_leads": base.filter(lead_status=Customer.LeadStatus.COLD).count(),
            "new_this_month": new_this_month,
            "archived": archived,
        }

    @staticmethod
    def find_duplicates(organization, phone=None, email=None, name=None):
        queryset = Customer.objects.filter(organization=organization)
        duplicates = []
        if phone:
            exact_phone = queryset.filter(phone=phone)
            for cust in exact_phone:
                duplicates.append({
                    "match_field": "phone",
                    "match_value": phone,
                    "existing_customer": {
                        "id": cust.id,
                        "customer_code": cust.customer_code,
                        "name": f"{cust.first_name} {cust.last_name}",
                        "phone": cust.phone,
                        "email": cust.email,
                    },
                })
        if email:
            exact_email = queryset.filter(email__iexact=email)
            for cust in exact_email:
                duplicates.append({
                    "match_field": "email",
                    "match_value": email,
                    "existing_customer": {
                        "id": cust.id,
                        "customer_code": cust.customer_code,
                        "name": f"{cust.first_name} {cust.last_name}",
                        "phone": cust.phone,
                        "email": cust.email,
                    },
                })
        if name:
            name_parts = name.split()
            if name_parts:
                q = Q()
                for part in name_parts:
                    q |= Q(first_name__icontains=part) | Q(last_name__icontains=part)
                name_matches = queryset.filter(q)
                for cust in name_matches:
                    duplicates.append({
                        "match_field": "name",
                        "match_value": name,
                        "existing_customer": {
                            "id": cust.id,
                            "customer_code": cust.customer_code,
                            "name": f"{cust.first_name} {cust.last_name}",
                            "phone": cust.phone,
                            "email": cust.email,
                        },
                    })
        return duplicates

    @staticmethod
    def get_timeline(organization, customer_id):
        customer = CustomerSelector.get_customer(organization, customer_id)
        if not customer:
            return []
        activities = CustomerActivity.objects.filter(organization=organization, customer=customer).order_by("-timestamp")
        notes = CustomerNote.objects.filter(organization=organization, customer=customer).order_by("-created_at")
        timeline = []
        for activity in activities:
            timeline.append({
                "id": activity.id,
                "type": "activity",
                "activity": activity.activity,
                "description": activity.description,
                "performed_by": str(activity.performed_by) if activity.performed_by else None,
                "timestamp": activity.timestamp,
            })
        for note in notes:
            timeline.append({
                "id": note.id,
                "type": "note",
                "note": note.note,
                "created_by": str(note.created_by) if note.created_by else None,
                "created_at": note.created_at,
            })
        from dateutil import parser as date_parser
        timeline.sort(key=lambda x: x.get("timestamp") or x.get("created_at"), reverse=True)
        return timeline

    @staticmethod
    def get_categories(organization):
        return CustomerCategory.objects.filter(organization=organization)

    @staticmethod
    def get_lists(organization):
        return CustomerList.objects.filter(organization=organization)

    @staticmethod
    def get_list(organization, list_id):
        return CustomerList.objects.filter(organization=organization, id=list_id).first()

    @staticmethod
    def get_list_customers(organization, list_id):
        customer_list = CustomerSelector.get_list(organization, list_id)
        if not customer_list:
            return CustomerListCustomer.objects.none()
        return CustomerListCustomer.objects.filter(organization=organization, customer_list=customer_list)
