import csv
import io
from django.db import transaction
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


class CustomerService:
    @staticmethod
    @transaction.atomic
    def create_customer(organization, created_by=None, **kwargs):
        customer = Customer.objects.create(
            organization=organization,
            created_by=created_by,
            **kwargs,
        )
        CustomerService.log_activity(
            organization=organization,
            customer_id=customer.id,
            activity=CustomerActivity.ActivityType.CUSTOMER_CREATED,
            performed_by=created_by,
            description=f"Customer created by {created_by.get_full_name() or created_by.username if created_by else 'System'}",
        )
        return customer

    @staticmethod
    @transaction.atomic
    def update_customer(organization, customer_id, **kwargs):
        customer = Customer.objects.get(organization=organization, id=customer_id)
        old_lead_status = customer.lead_status
        old_assigned_employee = customer.assigned_employee_id

        for key, value in kwargs.items():
            setattr(customer, key, value)
        customer.save()

        updated_by = kwargs.pop("updated_by", None)
        if old_lead_status != customer.lead_status:
            CustomerService.log_activity(
                organization=organization,
                customer_id=customer.id,
                activity=CustomerActivity.ActivityType.STATUS_CHANGED,
                performed_by=updated_by,
                description=f"Status changed from {old_lead_status} to {customer.lead_status}",
            )
        if old_assigned_employee != customer.assigned_employee_id:
            CustomerService.log_activity(
                organization=organization,
                customer_id=customer.id,
                activity=CustomerActivity.ActivityType.ASSIGNED,
                performed_by=updated_by,
                description=f"Customer assigned to {customer.assigned_employee}",
            )

        return customer

    @staticmethod
    @transaction.atomic
    def archive_customer(organization, customer_id, archived_by=None):
        customer = Customer.objects.get(organization=organization, id=customer_id)
        customer.is_archived = True
        customer.save(update_fields=["is_archived", "updated_at"])
        CustomerService.log_activity(
            organization=organization,
            customer_id=customer.id,
            activity=CustomerActivity.ActivityType.ARCHIVED,
            performed_by=archived_by,
            description=f"Customer archived by {archived_by.get_full_name() or archived_by.username if archived_by else 'System'}",
        )

    @staticmethod
    @transaction.atomic
    def restore_customer(organization, customer_id, restored_by=None):
        customer = Customer.objects.get(organization=organization, id=customer_id)
        customer.is_archived = False
        customer.save(update_fields=["is_archived", "updated_at"])
        CustomerService.log_activity(
            organization=organization,
            customer_id=customer.id,
            activity=CustomerActivity.ActivityType.RESTORED,
            performed_by=restored_by,
            description=f"Customer restored by {restored_by.get_full_name() or restored_by.username if restored_by else 'System'}",
        )

    @staticmethod
    @transaction.atomic
    def soft_delete_customer(organization, customer_id, deleted_by=None):
        customer = Customer.objects.get(organization=organization, id=customer_id)
        from django.utils import timezone
        customer.deleted_at = timezone.now()
        customer.is_archived = True
        customer.save(update_fields=["deleted_at", "is_archived", "updated_at"])

    @staticmethod
    @transaction.atomic
    def log_activity(organization, customer_id, activity, performed_by=None, description=""):
        return CustomerActivity.objects.create(
            organization=organization,
            customer_id=customer_id,
            activity=activity,
            performed_by=performed_by,
            description=description,
        )

    @staticmethod
    @transaction.atomic
    def add_note(organization, customer_id, note, created_by=None):
        note_obj = CustomerNote.objects.create(
            organization=organization,
            customer_id=customer_id,
            note=note,
            created_by=created_by,
        )
        CustomerService.log_activity(
            organization=organization,
            customer_id=customer_id,
            activity=CustomerActivity.ActivityType.NOTE_ADDED,
            performed_by=created_by,
            description=note[:200],
        )
        return note_obj

    @staticmethod
    @transaction.atomic
    def create_category(organization, name, description="", color="#6366f1", created_by=None):
        return CustomerCategory.objects.create(
            organization=organization,
            name=name,
            description=description,
            color=color,
            created_by=created_by,
        )

    @staticmethod
    @transaction.atomic
    def create_list(organization, name, description="", created_by=None, customer_ids=None):
        customer_list = CustomerList.objects.create(
            organization=organization,
            name=name,
            description=description,
            created_by=created_by,
        )
        if customer_ids:
            customers = Customer.objects.filter(organization=organization, id__in=customer_ids)
            for customer in customers:
                CustomerListCustomer.objects.get_or_create(
                    organization=organization,
                    customer_list=customer_list,
                    customer=customer,
                )
        customer_list.update_count()
        return customer_list

    @staticmethod
    @transaction.atomic
    def add_to_list(organization, list_id, customer_ids):
        customer_list = CustomerList.objects.get(organization=organization, id=list_id)
        customers = Customer.objects.filter(organization=organization, id__in=customer_ids)
        added = 0
        for customer in customers:
            _, created = CustomerListCustomer.objects.get_or_create(
                organization=organization,
                customer_list=customer_list,
                customer=customer,
            )
            if created:
                added += 1
        customer_list.update_count()
        return added

    @staticmethod
    @transaction.atomic
    def remove_from_list(organization, list_id, customer_ids):
        customer_list = CustomerList.objects.get(organization=organization, id=list_id)
        removed = CustomerListCustomer.objects.filter(
            organization=organization,
            customer_list=customer_list,
            customer_id__in=customer_ids,
        ).delete()
        customer_list.update_count()
        return removed[0]

    @staticmethod
    @transaction.atomic
    def bulk_import(organization, parsed_rows, source_type=Customer.SourceType.CSV_IMPORT, imported_by=None):
        created_count = 0
        duplicate_count = 0
        invalid_count = 0
        errors = []

        for i, row in enumerate(parsed_rows):
            raw_first_name = (row.get("first_name") or row.get("Name") or row.get("first_name") or "").strip()
            raw_last_name = (row.get("last_name") or "").strip()
            phone = (row.get("Phone") or row.get("phone") or "").strip()
            email = (row.get("Email") or row.get("email") or "").strip()
            city = (row.get("City") or row.get("city") or "").strip()
            lead_status = (row.get("lead_status") or row.get("Status") or "NEW").upper()
            priority = (row.get("priority") or row.get("Priority") or "MEDIUM").upper()
            property_type = (row.get("property_type") or row.get("Property Type") or "").upper()
            budget_min = row.get("budget_min") or row.get("Budget Min")
            budget_max = row.get("budget_max") or row.get("Budget Max")
            company = row.get("company") or row.get("Company") or ""
            occupation = row.get("occupation") or row.get("Occupation") or ""
            purpose = (row.get("purpose") or row.get("Purpose") or "").upper()

            if not raw_first_name or not phone:
                invalid_count += 1
                errors.append(f"Row {i+1}: Missing required fields (Name, Phone)")
                continue

            existing = Customer.objects.filter(organization=organization, phone=phone).first()
            if existing:
                duplicate_count += 1
                continue

            try:
                if raw_last_name:
                    first = raw_first_name
                    last = raw_last_name
                else:
                    parts = raw_first_name.split(None, 1)
                    first = parts[0]
                    last = parts[1] if len(parts) > 1 else ""

                valid_statuses = [c[0] for c in Customer.LeadStatus.choices]
                if lead_status not in valid_statuses:
                    lead_status = Customer.LeadStatus.NEW

                valid_priorities = [c[0] for c in Customer.Priority.choices]
                if priority not in valid_priorities:
                    priority = Customer.Priority.MEDIUM

                customer = Customer.objects.create(
                    organization=organization,
                    created_by=imported_by,
                    first_name=first,
                    last_name=last,
                    email=email,
                    phone=phone,
                    lead_status=lead_status,
                    priority=priority,
                    company=company,
                    occupation=occupation,
                    source_type=source_type,
                    source_notes=f"Bulk imported from CSV row {i+1}",
                )

                if city:
                    CustomerAddress.objects.create(
                        organization=organization,
                        customer=customer,
                        city=city,
                        country="India",
                    )

                try:
                    b_min = float(budget_min) if budget_min else None
                except (ValueError, TypeError):
                    b_min = None

                try:
                    b_max = float(budget_max) if budget_max else None
                except (ValueError, TypeError):
                    b_max = None

                if property_type or b_min or b_max or purpose or city:
                    CustomerRequirement.objects.create(
                        organization=organization,
                        customer=customer,
                        property_type=property_type,
                        budget_min=b_min,
                        budget_max=b_max,
                        purpose=purpose,
                        preferred_city=city,
                    )

                created_count += 1
            except Exception as e:
                invalid_count += 1
                errors.append(f"Row {i+1}: {str(e)}")

        return {
            "created": created_count,
            "duplicates": duplicate_count,
            "invalid": invalid_count,
            "errors": errors,
        }

    @staticmethod
    def parse_csv(file_content):
        reader = csv.DictReader(io.StringIO(file_content))
        return list(reader)

    @staticmethod
    def parse_excel(file_path):
        try:
            import openpyxl
            workbook = openpyxl.load_workbook(file_path)
            sheet = workbook.active
            headers = [str(cell).strip() for cell in sheet[1]]
            rows = []
            for row in sheet.iter_rows(min_row=2, values_only=True):
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = str(row[i]) if i < len(row) and row[i] is not None else ""
                rows.append(row_dict)
            return rows
        except ImportError:
            import pandas as pd
            df = pd.read_excel(file_path)
            return df.to_dict(orient="records")
