from django.db import transaction
from django.contrib.auth.models import User
from apps.pipeline.models import PipelineStage, Deal
from apps.contacts.models import Contact
from apps.companies.models import Company
from apps.audit.services import ActivityLogService


class PipelineService:
    @staticmethod
    @transaction.atomic
    def create_stage(organization, user, name, order=0):
        stage = PipelineStage.objects.create(
            organization=organization,
            name=name,
            order=order,
        )
        return stage

    @staticmethod
    @transaction.atomic
    def create_deal(
        organization,
        user,
        title,
        stage_id,
        amount=0.0,
        close_date=None,
        assigned_to_id=None,
        contact_id=None,
        company_id=None,
    ):
        stage = PipelineStage.objects.get(organization=organization, id=stage_id)
        assigned_to = User.objects.get(id=assigned_to_id) if assigned_to_id else None
        contact = Contact.objects.get(organization=organization, id=contact_id) if contact_id else None
        company = Company.objects.get(organization=organization, id=company_id) if company_id else None

        deal = Deal.objects.create(
            organization=organization,
            title=title,
            stage=stage,
            amount=amount,
            close_date=close_date,
            assigned_to=assigned_to,
            contact=contact,
            company=company,
        )

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="deal_created",
            target_type="deal",
            target_id=deal.id,
            description=f"Deal '{deal.title}' was created under stage '{stage.name}'.",
        )
        return deal

    @staticmethod
    @transaction.atomic
    def update_deal(organization, user, deal_id, **fields):
        deal = Deal.objects.get(organization=organization, id=deal_id)
        old_stage = deal.stage.name

        for field, value in fields.items():
            if field == "stage_id":
                deal.stage = PipelineStage.objects.get(organization=organization, id=value)
            elif field == "assigned_to_id":
                deal.assigned_to = User.objects.get(id=value) if value else None
            elif field == "contact_id":
                deal.contact = Contact.objects.get(organization=organization, id=value) if value else None
            elif field == "company_id":
                deal.company = Company.objects.get(organization=organization, id=value) if value else None
            elif hasattr(deal, field):
                setattr(deal, field, value)

        deal.save()

        # Log specific action for stage movement
        if deal.stage.name != old_stage:
            ActivityLogService.log_activity(
                organization=organization,
                user=user,
                action="deal_stage_changed",
                target_type="deal",
                target_id=deal.id,
                description=f"Deal '{deal.title}' stage changed from '{old_stage}' to '{deal.stage.name}'.",
            )
        else:
            ActivityLogService.log_activity(
                organization=organization,
                user=user,
                action="deal_updated",
                target_type="deal",
                target_id=deal.id,
                description=f"Deal '{deal.title}' details were updated.",
            )
        return deal

    @staticmethod
    @transaction.atomic
    def delete_deal(organization, user, deal_id):
        deal = Deal.objects.get(organization=organization, id=deal_id)
        title = deal.title
        deal.delete()

        ActivityLogService.log_activity(
            organization=organization,
            user=user,
            action="deal_deleted",
            target_type="deal",
            target_id=deal_id,
            description=f"Deal '{title}' was deleted.",
        )
        return True
