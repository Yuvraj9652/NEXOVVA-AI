import os
import json
import urllib.request
import urllib.error
from django.conf import settings
from django.db import transaction
from django.contrib.auth.models import User

from apps.ai.models import ChatSession, ChatMessage, AIUsage, PromptTemplate
from apps.organizations.models import Organization


class GeminiService:
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    @staticmethod
    def get_api_key():
        return getattr(settings, "GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))

    @classmethod
    def calculate_cost(cls, prompt_tokens, completion_tokens):
        # Pricing for gemini-1.5-flash:
        # Prompt: $0.075 per 1M tokens ($0.000000075/token)
        # Completion: $0.30 per 1M tokens ($0.00000030/token)
        prompt_cost = prompt_tokens * 0.000000075
        completion_cost = completion_tokens * 0.00000030
        return prompt_cost + completion_cost

    @classmethod
    def call_gemini(cls, contents, system_instruction=None):
        api_key = cls.get_api_key()
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not configured.")

        url = f"{cls.API_URL}?key={api_key}"
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
            }
        }
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        headers = {"Content-Type": "application/json"}
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as response:
                res_data = json.loads(response.read().decode("utf-8"))
                
                # Extract text and token metadata
                candidate = res_data.get("candidates", [{}])[0]
                text_content = candidate.get("content", {}).get("parts", [{}])[0].get("text", "")
                
                usage = res_data.get("usageMetadata", {})
                prompt_tokens = usage.get("promptTokenCount", 0)
                completion_tokens = usage.get("candidatesTokenCount", 0)
                
                return text_content, prompt_tokens, completion_tokens
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode("utf-8")
            try:
                error_json = json.loads(error_msg)
                message = error_json.get("error", {}).get("message", "API Error")
            except Exception:
                message = error_msg
            raise RuntimeError(f"Gemini API Error: {message}")
        except Exception as e:
            raise RuntimeError(f"Failed to call Gemini: {str(e)}")

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

        # Build contents from session history
        history = ChatMessage.objects.filter(session=session).order_by("created_at")
        contents = []
        for msg in history:
            role = "user" if msg.role == ChatMessage.Roles.USER else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })

        system_prompt = (
            "You are NEXOVA AI, an elite Real Estate CRM assistant. "
            "You help real estate agents manage leads, create email templates, structure property sales arguments, "
            "and organize tasks. Keep answers professional, concise, and structured."
        )

        text_response, prompt_tokens, completion_tokens = cls.call_gemini(
            contents=contents,
            system_instruction=system_prompt
        )

        # Save assistant message
        ChatMessage.objects.create(
            session=session,
            role=ChatMessage.Roles.ASSISTANT,
            content=text_response
        )

        # Save usage stats
        cost = cls.calculate_cost(prompt_tokens, completion_tokens)
        AIUsage.objects.create(
            organization=organization,
            user=user,
            model_name="gemini-1.5-flash",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
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

        # Resolve variables
        prompt_text = prompt_temp.template
        for key, value in variables.items():
            prompt_text = prompt_text.replace(f"{{{{{key}}}}}", str(value))

        contents = [{"role": "user", "parts": [{"text": prompt_text}]}]
        text_response, prompt_tokens, completion_tokens = cls.call_gemini(contents=contents)

        cost = cls.calculate_cost(prompt_tokens, completion_tokens)
        AIUsage.objects.create(
            organization=organization,
            user=user,
            model_name="gemini-1.5-flash",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
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

        prompt = (
            f"Analyze this buyer lead and recommend the best matching units from our database:\n"
            f"Lead Requirement Title: {lead.title}\n"
            f"Lead Budget: {lead.budget or 'Not specified'}\n"
            f"Lead Preferences (Interaction history / notes):\n{lead.notes}\n\n"
            f"Available property inventory database:\n{json.dumps(units_list, indent=2)}\n\n"
            f"Pick the top 2 best fitting units. For each, output in a structured readable format:\n"
            f"1. Property Name & ID\n"
            f"2. A percentage match score (e.g., 95% Match)\n"
            f"3. Bullet points explaining exactly why this property matches their budget, timeline, and size requirements."
        )

        contents = [{"role": "user", "parts": [{"text": prompt}]}]
        system_instruction = (
            "You are a professional real estate matchmaker. "
            "Evaluate listings objectively against lead budget and criteria. Keep recommendations clear and professional."
        )

        text_response, prompt_tokens, completion_tokens = GeminiService.call_gemini(
            contents=contents,
            system_instruction=system_instruction
        )

        # Log AI Usage
        cost = GeminiService.calculate_cost(prompt_tokens, completion_tokens)
        AIUsage.objects.create(
            organization=organization,
            user=user,
            model_name="gemini-1.5-flash",
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost=cost
        )

        return text_response
