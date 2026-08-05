import logging
from django.db import transaction
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.customers.models import Customer
from apps.notes.models import Note
from apps.tasks.models import Task
from apps.accounts.models import UserProfile

User = get_user_model()
logger = logging.getLogger("crm_service")


class CRMService:
    @classmethod
    @transaction.atomic
    def process_qualification_result(
        cls, organization, customer: Customer, lead_stage: str, buying_intent: str, needs_human: bool, summary: str
    ) -> None:
        """
        Consumes the structured result of an AI conversation, updates the Customer lead stage,
        logs interaction notes, and generates salesperson tasks if handoff is requested.
        """
        logger.info(f"CRMService processing qualification for Customer: {customer.id} in Org: {organization.id}")

        # 1. Update Customer Lead Status if a progression is suggested
        # Map AI suggested stages to Customer.LeadStatus model choices
        stage_mapping = {
            "NEW": Customer.LeadStatus.NEW,
            "CONTACTED": Customer.LeadStatus.CONTACTED,
            "QUALIFIED": Customer.LeadStatus.VISITED,  # Maps QUALIFIED to intermediate lead state VISITED/NEGOTIATION
            "LOST": Customer.LeadStatus.LOST,
            "BOOKED": Customer.LeadStatus.BOOKED
        }
        
        target_status = stage_mapping.get(lead_stage)
        if target_status and customer.lead_status != target_status:
            customer.lead_status = target_status
            customer.save(update_fields=["lead_status", "updated_at"])
            logger.info(f"Customer {customer.id} lead_status updated to {target_status}")

        # 2. Find a valid author for the CRM Note
        # Resolve to any active organization user profile, falling back to the first user
        profile = UserProfile.objects.filter(organization=organization).first()
        author = profile.user if profile else User.objects.first()

        if not author:
            logger.warning("No user found in the database. CRM Note creation skipped.")
            return

        # 3. Create Note link to Customer
        Note.objects.create(
            organization=organization,
            content=f"[AI Interaction Summary]\nIntent/Buying Intent: {buying_intent}\nAI Response: {summary}",
            customer=customer,
            author=author
        )
        logger.info(f"CRM Note created successfully for Customer {customer.id}")

        # 4. Generate Task/Notification if agent handoff is required
        if needs_human:
            # Determine assignee: the assigned employee's user account, or the default organization user
            assignee = None
            if customer.assigned_employee and hasattr(customer.assigned_employee, "user"):
                assignee = customer.assigned_employee.user
            if not assignee:
                assignee = author

            task_title = f"Follow-up request: {customer.first_name} {customer.last_name}"
            due_date = timezone.now() + timezone.timedelta(days=1)

            Task.objects.create(
                organization=organization,
                title=task_title,
                description=(
                    f"AI has flagged this conversation for human takeover.\n"
                    f"Customer Email: {customer.email}\n"
                    f"Customer Phone: {customer.phone}\n"
                    f"Latest AI reply summary: {summary}"
                ),
                assigned_to=assignee,
                due_date=due_date,
                completed=False
            )
            logger.info(f"Follow-up task created and assigned to User {assignee.username if assignee else 'System'}")
