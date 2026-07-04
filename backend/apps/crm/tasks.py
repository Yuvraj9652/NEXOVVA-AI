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
        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        system_instruction = (
            "You are a professional real estate analyst. "
            "You MUST output valid, parsable JSON matching the requested schema. "
            "Do not include any preambles, postambles, or markdown formatting."
        )

        response_text, prompt_tokens, completion_tokens = GeminiService.call_gemini(
            contents=contents,
            system_instruction=system_instruction,
        )

        # Clean markdown formatting if returned
        cleaned_text = response_text.strip()
        if cleaned_text.startswith("```"):
            cleaned_text = cleaned_text.split("\n", 1)[1]
        if cleaned_text.endswith("```"):
            cleaned_text = cleaned_text.rsplit("\n", 1)[0]
        cleaned_text = cleaned_text.strip()
        if cleaned_text.startswith("json"):
            cleaned_text = cleaned_text[4:].strip()

        data = json.loads(cleaned_text)

        # Update lead
        lead.score = data.get("score", lead.score)
        if data.get("budget_estimate") and not lead.budget:
            lead.budget = data.get("budget_estimate")

        # Append structured analysis to notes
        summary = data.get("needs_summary", "")
        if summary:
            lead.notes = f"{lead.notes}\n\n[AI Lead Enrichment Details]:\n{summary}\nScore: {lead.score}/100"

        lead.save()

        # Log usage of AI
        cost = GeminiService.calculate_cost(prompt_tokens, completion_tokens)
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
