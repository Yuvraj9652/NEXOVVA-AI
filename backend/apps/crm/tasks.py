import json
import logging
from celery import shared_task
from apps.leads.models import Lead
from apps.notes.models import Note
from apps.ai.services import GeminiService

logger = logging.getLogger(__name__)


@shared_task
def enrich_lead_via_ai(lead_id):
    """Asynchronously enrich lead details and compute purchase intent score via Google Gemini."""
    try:
        lead = Lead.objects.select_related("organization").get(id=lead_id)
    except Lead.DoesNotExist:
        logger.error(f"Lead with ID {lead_id} does not exist.")
        return False

    notes = Note.objects.filter(lead=lead)
    notes_text = "\n".join([f"- {note.content}" for note in notes])
    if not notes_text:
        notes_text = "No notes available."

    prompt = (
        f"Analyze the following real estate lead details:\n"
        f"Lead Title: {lead.title}\n"
        f"Budget set by agent: {lead.budget or 'Not specified'}\n"
        f"Timeline / Interactions history:\n{notes_text}\n\n"
        f"Provide a structured analysis in JSON format. Do not return markdown, just raw JSON.\n"
        f"JSON Schema:\n"
        f"{{\n"
        f"  \"score\": <int between 0 and 100 based on lead interest/purchase capability>,\n"
        f"  \"budget_estimate\": <float or null representing estimated budget extracted from interactions>,\n"
        f"  \"needs_summary\": \"<string summarizing needs, preferences, timeline>\"\n"
        f"}}"
    )

    try:
        payload = {
            "customer_name": f"{lead.contact.first_name} {lead.contact.last_name}" if lead.contact else lead.title,
            "budget": str(lead.budget) if lead.budget else "Not specified",
            "timeline": notes_text,
            "interest_level": lead.status,
            "property_type": lead.title
        }

        data = GeminiService._call_ai_service("/lead-score/", payload)

        # Update lead
        lead.score = data.get("score", lead.score)

        # Append structured analysis to notes
        summary = data.get("reason", "")
        category = data.get("category", "")
        if summary:
            lead.notes = f"{lead.notes}\n\n[AI Lead Qualification Details]:\nCategory: {category}\nScore: {lead.score}/100\nReasoning: {summary}"

        lead.save()

        # Log usage of AI
        cost = GeminiService.calculate_cost(200, 100)
        from apps.ai.models import AIUsage
        from django.contrib.auth.models import User
        # Default to first admin in org if no specific user triggers background task
        admin_user = User.objects.filter(userprofile__organization=lead.organization, userprofile__role="ADMIN").first()
        if admin_user:
            AIUsage.objects.create(
                organization=lead.organization,
                user=admin_user,
                model_name="gemini-1.5-flash",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost=cost,
            )

        logger.info(f"Successfully enriched lead {lead_id} (AI Score: {lead.score})")
        return True
    except Exception as e:
        logger.error(f"Failed to enrich lead {lead_id}: {str(e)}")
        return False
