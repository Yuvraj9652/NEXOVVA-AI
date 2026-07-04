from django.db import transaction
from django.db.models import Count
from apps.leads.models import Lead
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.employees.models import Employee
from apps.audit.services import ActivityLogService


class LeadAssignmentEngine:
    @staticmethod
    def assign_lead(organization, lead):
        """Assigns a lead to an active employee who has the fewest assigned contacts."""
        employees = Employee.objects.filter(
            organization=organization,
            status=Employee.Statuses.ACTIVE
        ).select_related("user")

        if not employees.exists():
            return None

        # Annotate employees with count of assigned contacts to identify least loaded agent
        annotated = employees.annotate(
            lead_count=Count("user__assigned_contacts")
        ).order_by("lead_count")

        assigned_employee = annotated.first()
        if assigned_employee and lead.contact:
            lead.contact.assigned_to = assigned_employee.user
            lead.contact.save()
            return assigned_employee.user
        return None


class LeadService:
    @staticmethod
    @transaction.atomic
    def create_lead(
        organization,
        user,
        title,
        contact_id=None,
        company_id=None,
        status=Lead.Statuses.NEW,
        source=Lead.Sources.OTHER,
        budget=None,
        notes="",
        score=50,
    ):
        contact = Contact.objects.get(organization=organization, id=contact_id) if contact_id else None
        company = Company.objects.get(organization=organization, id=company_id) if company_id else None

        lead = Lead.objects.create(
            organization=organization,
            title=title,
            contact=contact,
            company=company,
            status=status,
            source=source,
            budget=budget,
            notes=notes,
            score=score,
        )

        # Run lead assignment engine
        assigned_user = LeadAssignmentEngine.assign_lead(organization, lead)
        assigned_name = assigned_user.username if assigned_user else "Unassigned"

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="lead_created",
            target_type="lead",
            target_id=lead.id,
            description=f"Lead '{lead.title}' was created and assigned to {assigned_name}.",
        )

        # Trigger event dispatch via the Event Bus once the transaction commits
        from apps.automation.services import EventBus
        transaction.on_commit(
            lambda: EventBus.dispatch_event(organization, user, "lead_created", lead.id)
        )
        return lead

    @staticmethod
    @transaction.atomic
    def update_lead(organization, user, lead_id, **fields):
        lead = Lead.objects.get(organization=organization, id=lead_id)

        for field, value in fields.items():
            if field == "contact_id":
                lead.contact = Contact.objects.get(organization=organization, id=value) if value else None
            elif field == "company_id":
                lead.company = Company.objects.get(organization=organization, id=value) if value else None
            elif hasattr(lead, field):
                setattr(lead, field, value)

        lead.save()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="lead_updated",
            target_type="lead",
            target_id=lead.id,
            description=f"Lead '{lead.title}' was updated.",
        )
        return lead

    @staticmethod
    @transaction.atomic
    def delete_lead(organization, user, lead_id):
        lead = Lead.objects.get(organization=organization, id=lead_id)
        title = lead.title
        lead.delete()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="lead_deleted",
            target_type="lead",
            target_id=lead_id,
            description=f"Lead '{title}' was deleted.",
        )
        return True
