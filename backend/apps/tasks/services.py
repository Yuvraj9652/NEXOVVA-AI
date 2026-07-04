from django.db import transaction
from django.contrib.auth.models import User
from apps.tasks.models import Task
from apps.contacts.models import Contact
from apps.pipeline.models import Deal
from apps.leads.models import Lead
from apps.audit.services import ActivityLogService


class TasksService:
    @staticmethod
    @transaction.atomic
    def create_task(
        organization,
        user,
        title,
        description="",
        due_date=None,
        completed=False,
        assigned_to_id=None,
        contact_id=None,
        deal_id=None,
        lead_id=None,
    ):
        assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None
        contact = Contact.objects.get(organization=organization, id=contact_id) if contact_id else None
        deal = Deal.objects.get(organization=organization, id=deal_id) if deal_id else None
        lead = Lead.objects.get(organization=organization, id=lead_id) if lead_id else None

        task = Task.objects.create(
            organization=organization,
            title=title,
            description=description,
            due_date=due_date,
            completed=completed,
            assigned_to=assigned_to,
            contact=contact,
            deal=deal,
            lead=lead,
        )

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="task_created",
            target_type="task",
            target_id=task.id,
            description=f"Task '{task.title}' was created.",
        )
        return task

    @staticmethod
    @transaction.atomic
    def update_task(organization, user, task_id, **fields):
        task = Task.objects.get(organization=organization, id=task_id)

        for field, value in fields.items():
            if field == "assigned_to_id":
                task.assigned_to = User.objects.get(id=value) if value else None
            elif field == "contact_id":
                task.contact = Contact.objects.get(organization=organization, id=value) if value else None
            elif field == "deal_id":
                task.deal = Deal.objects.get(organization=organization, id=value) if value else None
            elif field == "lead_id":
                task.lead = Lead.objects.get(organization=organization, id=value) if value else None
            elif hasattr(task, field):
                setattr(task, field, value)

        task.save()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="task_updated",
            target_type="task",
            target_id=task.id,
            description=f"Task '{task.title}' was updated.",
        )
        return task

    @staticmethod
    @transaction.atomic
    def delete_task(organization, user, task_id):
        task = Task.objects.get(organization=organization, id=task_id)
        title = task.title
        task.delete()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="task_deleted",
            target_type="task",
            target_id=task_id,
            description=f"Task '{title}' was deleted.",
        )
        return True
