import os
import json
import urllib.request
import urllib.error
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model

from apps.ai.models import ChatSession, ChatMessage, AIUsage, PromptTemplate
from apps.organizations.models import Organization

User = get_user_model()

class GeminiService:
    API_URL = "http://127.0.0.1:8001"

    @classmethod
    def _call_ai_service(cls, path, payload):
        import urllib.request
        import urllib.error
        import json
        
        url = f"{cls.API_URL}{path}"
        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode("utf-8")
            raise RuntimeError(f"AI Service HTTP Error: {error_msg}")
        except Exception as e:
            raise RuntimeError(f"Failed to call AI Service: {str(e)}")

    @classmethod
    def calculate_cost(cls, prompt_tokens, completion_tokens):
        prompt_cost = prompt_tokens * 0.000000075
        completion_cost = completion_tokens * 0.00000030
        return prompt_cost + completion_cost

    @classmethod
    @transaction.atomic
    def generate_chat_response(cls, organization, user, session_id, user_message_text):
        session = ChatSession.objects.get(organization=organization, id=session_id)
        
        # Save user message
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.Roles.USER,
            content=user_message_text
        )

        # Call FastAPI AI chat
        payload = {
            "session_id": str(session_id),
            "message": user_message_text
        }
        res_data = cls._call_ai_service("/chat/", payload)
        text_response = res_data.get("response", "")

        # Save assistant message
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.Roles.ASSISTANT,
            content=text_response
        )

        # Save usage stats
        cost = cls.calculate_cost(200, 150)
        AIUsage.objects.create(
            organization=organization,
            user=user,
            model_name="gemini-2.5-flash",
            prompt_tokens=200,
            completion_tokens=150,
            cost=cost
        )

        # Touch session to update its timestamp
        session.save()

        return text_response

    @classmethod
    @transaction.atomic
    def run_prompt_template(cls, organization, user, template_name, variables):
        try:
            prompt_temp = PromptTemplate.objects.get(name=template_name)
        except PromptTemplate.DoesNotExist:
            raise ValueError(f"Prompt template '{template_name}' not found.")

        prompt_text = prompt_temp.template
        for key, value in variables.items():
            prompt_text = prompt_text.replace(f"{{{{{key}}}}}", str(value))

        payload = {
            "message": prompt_text,
            "session_id": "template_run"
        }
        res_data = cls._call_ai_service("/chat/", payload)
        text_response = res_data.get("response", "")

        cost = cls.calculate_cost(100, 100)
        AIUsage.objects.create(
            organization=organization,
            user=user,
            model_name="gemini-2.5-flash",
            prompt_tokens=100,
            completion_tokens=100,
            cost=cost
        )

        return text_response


class PropertyMatchmakerService:
    @classmethod
    def match_properties_for_lead(cls, organization, user, lead_id):
        from apps.leads.models import Lead
        from apps.properties.models import Unit

        lead = Lead.objects.get(organization=organization, id=lead_id)
        units = Unit.objects.filter(organization=organization, status=Unit.Statuses.AVAILABLE).select_related("project")

        if not units.exists():
            return "No available properties found in the inventory."

        units_list = []
        for u in units:
            project_name = u.project.name if u.project else "Independent"
            units_list.append({
                "id": u.id,
                "name": u.name,
                "project": project_name,
                "price": float(u.price),
                "bedrooms": u.bedrooms,
                "bathrooms": u.bathrooms,
                "area_sqft": u.area_sqft,
                "address": u.address
            })

        payload = {
            "lead_title": lead.title,
            "lead_budget": float(lead.budget) if lead.budget else None,
            "lead_notes": lead.notes,
            "units": units_list
        }

        try:
            res_data = GeminiService._call_ai_service("/matching/match", payload)
            matches = res_data.get("matches", [])
            if not matches:
                return "No property matches found in database matching preferences."

            lines = ["Here are the top matching properties identified by NEXOVA AI:\n"]
            for m in matches:
                unit_obj = next((u for u in units_list if u["id"] == m["id"]), None)
                if unit_obj:
                    lines.append(f"- **{unit_obj['name']} ({unit_obj['project']})** - Match: {m['score']}%")
                    lines.append(f"  *Reason*: {m['reason']}")

            return "\n".join(lines)
        except Exception as e:
            return f"Property matching analysis failed: {str(e)}"

