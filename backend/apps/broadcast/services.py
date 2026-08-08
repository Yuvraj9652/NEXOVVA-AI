import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from apps.broadcast.models import (
    Campaign,
    CampaignMessage,
    CampaignLog,
    AudienceSegment,
    ContactList,
    BroadcastTemplate,
    CampaignAnalytics,
)
from apps.broadcast.repositories import BroadcastRepository
from apps.broadcast.selectors import BroadcastSelector
from apps.customers.models import Customer
from apps.properties.models import Project


class BroadcastService:
    """Service layer for Broadcast app."""

    @staticmethod
    def send_campaign_message(campaign, data):
        message = CampaignMessage.objects.create(
            organization=campaign.organization,
            campaign=campaign,
            customer_name=data.get("customer_name", ""),
            customer_phone=data.get("customer_phone", ""),
            customer_email=data.get("customer_email", ""),
            channel=data.get("channel", "whatsapp"),
            message=data.get("message", ""),
            status=CampaignMessage.MessageStatus.SENT,
        )
        BroadcastService.log_action(campaign, "SEND", f"Message sent to {message.customer_name} via {message.channel}")
        return {"id": message.id, "status": "sent", "customer_name": message.customer_name}

    @staticmethod
    def schedule_campaign(campaign, data):
        campaign.status = Campaign.Statuses.SCHEDULED
        campaign.schedule_time = data.get("schedule_time")
        campaign.recurring = data.get("recurring", False)
        campaign.timezone = data.get("timezone", "UTC")
        campaign.save()
        BroadcastService.log_action(campaign, "SCHEDULE", f"Campaign scheduled for {campaign.schedule_time}")
        return {"id": campaign.id, "status": "scheduled", "schedule_time": str(campaign.schedule_time)}

    @staticmethod
    def preview_campaign_message(campaign, data):
        channel = data.get("channel", "whatsapp")
        template = BroadcastTemplate.objects.filter(
            organization=campaign.organization,
            template_type__iexact=channel.upper(),
        ).first()
        message = template.__dict__.get(f"{channel}_template", "") if template else ""
        return {"channel": channel, "preview": message, "template_used": template.name if template else "Default"}

    @staticmethod
    def duplicate_campaign(organization, campaign, created_by):
        new_campaign = Campaign.objects.create(
            organization=organization,
            name=f"{campaign.name} (Copy)",
            campaign_type=campaign.campaign_type,
            project=campaign.project,
            status=Campaign.Statuses.DRAFT,
            audience_segment=campaign.audience_segment,
            contact_list=campaign.contact_list,
            channels=campaign.channels,
            ai_prompt=campaign.ai_prompt,
            message_versions=campaign.message_versions,
            schedule_time=campaign.schedule_time,
            recurring=campaign.recurring,
            timezone=campaign.timezone,
            created_by=created_by,
        )
        BroadcastService.log_action(new_campaign, "DUPLICATE", f"Duplicated from campaign {campaign.id}")
        return new_campaign

    @staticmethod
    def import_contacts(organization, data):
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile
        import csv
        import io

        file = data.get("file")
        list_name = data.get("list_name", "Imported Contacts")

        if not file:
            return {"error": "No file uploaded"}

        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)

        contact_list = ContactList.objects.create(
            organization=organization,
            name=list_name,
            created_by=organization.created_by if hasattr(organization, 'created_by') else None,
        )

        valid = 0
        invalid = 0
        duplicates = 0
        imported_contacts = []

        for row in rows:
            phone = row.get("Phone", row.get("phone", ""))
            email = row.get("Email", row.get("email", ""))
            name = row.get("Name", row.get("name", ""))

            if not phone and not email:
                invalid += 1
                continue

            if BroadcastRepository.check_duplicate_contact(organization, None, phone, email):
                duplicates += 1
                continue

            contact_list.contacts.append({
                "name": name,
                "phone": phone,
                "email": email,
                "city": row.get("City", row.get("city", "")),
                "budget": row.get("Budget", row.get("budget", "")),
                "configuration": row.get("Configuration", row.get("configuration", "")),
                "preferred_area": row.get("Preferred Area", row.get("preferred_area", "")),
                "lead_status": row.get("Lead Status", row.get("lead_status", "")),
                "tags": row.get("Tags", row.get("tags", "")),
            })
            valid += 1
            imported_contacts.append({"name": name, "phone": phone, "email": email})

        contact_list.save()

        return {
            "list_name": list_name,
            "total_records": len(rows),
            "valid": valid,
            "invalid": invalid,
            "duplicates": duplicates,
            "imported": imported_contacts,
            "contact_list_id": contact_list.id,
        }

    @staticmethod
    def ai_audience_match(organization, campaign_id, query, filters=None):
        campaign = BroadcastRepository.get_campaign_by_id(organization, campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        results = BroadcastSelector.get_audience_match_results(query, filters or {})
        customer_count = results.count()

        segment = AudienceSegment.objects.create(
            organization=organization,
            name=f"AI Match: {query[:50]}",
            segment_type=AudienceSegment.SegmentType.AI_MATCHED,
            filters={"query": query, "filters": filters or {}},
            customer_count=customer_count,
            created_by=organization.created_by if hasattr(organization, 'created_by') else None,
        )

        return {
            "segment_id": segment.id,
            "segment_name": segment.name,
            "query": query,
            "customer_count": customer_count,
            "filters": filters or {},
        }

    @staticmethod
    def ai_generate_content(organization, campaign_id, content_type, audience_segment=""):
        campaign = BroadcastRepository.get_campaign_by_id(organization, campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        project = campaign.project
        project_info = ""
        if project:
            project_info = f"""
Project Name: {project.name}
Builder: {project.builder}
City: {project.city}
Status: {project.status}
Property Type: {project.property_type}
Price Range: {project.starting_price} - {project.max_price}
Description: {project.short_description or project.description}
"""

        from ai_services.config.prompts import BROADCAST_CONTENT_PROMPT
        prompt = BROADCAST_CONTENT_PROMPT.format(
            content_type=content_type,
            campaign_name=campaign.name,
            project_info=project_info,
            audience_segment=audience_segment,
        )

        from ai_services.llm.router import generate_text
        try:
            generated = generate_text(prompt)
        except Exception as e:
            generated = f"Generated {content_type} content for campaign '{campaign.name}'."

        return {
            "content_type": content_type,
            "content": generated,
            "campaign_id": campaign_id,
        }

    @staticmethod
    def ai_personalize_message(organization, campaign_id, customer_name, customer_phone, customer_email, content_type):
        campaign = BroadcastRepository.get_campaign_by_id(organization, campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        project = campaign.project
        project_info = ""
        if project:
            project_info = f"""
Project: {project.name}
City: {project.city}
Price: {project.starting_price}
Builder: {project.builder}
"""

        from ai_services.config.prompts import BROADCAST_PERSONALIZE_PROMPT
        prompt = BROADCAST_PERSONALIZE_PROMPT.format(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            content_type=content_type,
            project_info=project_info,
            campaign_name=campaign.name,
        )

        from ai_services.llm.router import generate_text
        try:
            personalized = generate_text(prompt)
        except Exception as e:
            personalized = f"Hi {customer_name}, check out our new campaign '{campaign.name}'!"

        return {
            "customer_name": customer_name,
            "content_type": content_type,
            "personalized_message": personalized,
        }

    @staticmethod
    def ai_optimize_schedule(organization, campaign_id, audience_size):
        campaign = BroadcastRepository.get_campaign_by_id(organization, campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        from ai_services.config.prompts import BROADCAST_SCHEDULE_PROMPT
        prompt = BROADCAST_SCHEDULE_PROMPT.format(
            campaign_name=campaign.name,
            audience_size=audience_size,
            campaign_type=campaign.campaign_type,
        )

        from ai_services.llm.router import generate_json
        try:
            optimized = generate_json(prompt)
        except Exception as e:
            optimized = {"best_day": "Tuesday", "best_time": "10:00 AM", "best_channel": "WhatsApp"}

        return {
            "campaign_id": campaign_id,
            "recommendations": optimized,
        }

    @staticmethod
    def ai_check_duplicate(organization, campaign_id, customer_phone, customer_email):
        is_duplicate = BroadcastRepository.check_duplicate_contact(organization, campaign_id, customer_phone, customer_email)
        return {
            "customer_phone": customer_phone,
            "customer_email": customer_email,
            "is_duplicate": is_duplicate,
            "campaign_id": campaign_id,
        }

    @staticmethod
    def ai_follow_up(organization, campaign_id, customer_id, message_status, days_since_sent):
        campaign = BroadcastRepository.get_campaign_by_id(organization, campaign_id)
        if not campaign:
            return {"error": "Campaign not found"}

        from ai_services.config.prompts import BROADCAST_FOLLOWUP_PROMPT
        prompt = BROADCAST_FOLLOWUP_PROMPT.format(
            campaign_name=campaign.name,
            message_status=message_status,
            days_since_sent=days_since_sent,
        )

        from ai_services.llm.router import generate_json
        try:
            follow_up = generate_json(prompt)
        except Exception as e:
            follow_up = {"action": "send_reminder", "delay_days": 2, "message": "Follow up reminder"}

        return {
            "campaign_id": campaign_id,
            "customer_id": customer_id,
            "follow_up_action": follow_up,
        }

    @staticmethod
    def log_action(campaign, action, description=""):
        CampaignLog.objects.create(
            organization=campaign.organization,
            campaign=campaign,
            action=action,
            description=description,
            user=campaign.created_by,
        )
        return {"action": action, "logged": True}