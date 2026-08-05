import logging
from django.db import transaction
from apps.ai.models import AICustomerChatSession, AICustomerChatMessage, AIChatMemory
from apps.ai.ai_service import AIService
from apps.knowledge_base.models import ProjectDocument
from apps.crm.services import CRMService
from apps.analytics.analytics_dispatcher import AnalyticsDispatcher

logger = logging.getLogger("ai_service")


class ConversationEngine:
    @classmethod
    @transaction.atomic
    def process_message(cls, session: AICustomerChatSession, message_content: str) -> dict:
        """
        Processes an incoming customer message, runs state management, performs intent
        detection, conditionally queries project RAG documents, triggers LLM structured
        outputs, and coordinates downstream updates (CRM, Analytics).
        """
        logger.info(f"ConversationEngine processing message for Session: {session.id}")

        # 1. State Enforcement: If session is currently waiting for a human agent, bypass AI reply
        if session.status == AICustomerChatSession.Statuses.WAITING_FOR_AGENT:
            logger.info(f"Session {session.id} is in WAITING_FOR_AGENT state. AI reply bypassed.")
            return {
                "reply": "A sales representative has been notified and will get back to you shortly.",
                "state_changed": False,
                "needs_human": True
            }

        # Ensure session is active
        if session.status == AICustomerChatSession.Statuses.NEW:
            session.status = AICustomerChatSession.Statuses.ACTIVE
            session.save(update_fields=["status"])

        # Save incoming customer message
        AICustomerChatMessage.objects.create(
            session=session,
            role=AICustomerChatMessage.Roles.USER,
            content=message_content
        )

        # Get or create conversation memory
        memory, _ = AIChatMemory.objects.get_or_create(
            session=session,
            organization=session.organization
        )

        # 2. Intent Detection: Determine if RAG knowledge retrieval is required
        intent_schema = {
            "need_rag": "boolean indicating if message asks for specific project info/pricing/amenities/specs",
            "intent": "string choice (GREETING, INFORMATION_REQUEST, BOOKING_REQUEST, COMPLAINT, OTHER)"
        }
        intent_prompt = f"Detect customer intent from message: '{message_content}'"
        
        try:
            intent_data = AIService.generate_structured_output(intent_prompt, intent_schema)
            need_rag = intent_data.get("need_rag", False)
            detected_intent = intent_data.get("intent", "OTHER")
        except Exception as e:
            logger.error(f"Failed to detect intent: {e}")
            need_rag = True
            detected_intent = "INFORMATION_REQUEST"

        # 3. Retrieve Knowledge (RAG)
        rag_context = ""
        if need_rag and session.project:
            # Look up project documents
            doc = ProjectDocument.objects.filter(project=session.project, processed=True).first()
            if doc:
                try:
                    rag_context = AIService.ask_rag(
                        filename=doc.name,
                        question=message_content,
                        organization_id=session.organization.id
                    )
                    logger.info(f"RAG facts retrieved successfully from document: {doc.name}")
                except Exception as e:
                    logger.error(f"RAG query failed: {e}")
            
            # If no document or RAG query failed, fallback to project details
            if not rag_context:
                proj = session.project
                rag_context = (
                    f"Project: {proj.name}. Builder: {proj.builder}. City: {proj.city}. "
                    f"Property Type: {proj.property_type}. Starting Price: {proj.starting_price}. "
                    f"Max Price: {proj.max_price}. Description: {proj.short_description or proj.description}"
                )

        # 4. Load Conversation History
        history_msgs = AICustomerChatMessage.objects.filter(session=session).order_by("created_at")[:10]
        history_text = "\n".join([f"{msg.role}: {msg.content}" for msg in history_msgs])

        # 5. Build prompt and generate structured AI response
        structured_schema = {
            "reply": "The conversational reply to send to the customer.",
            "lead_stage": "CRM lead stage choice (NEW, CONTACTED, QUALIFIED, LOST, BOOKED)",
            "budget_min": "Min budget extracted (number/null)",
            "budget_max": "Max budget extracted (number/null)",
            "preferred_location": "Preferred location extracted (string/null)",
            "buying_intent": "HIGH, MEDIUM, or LOW buying intent scale",
            "needs_human": "boolean indicating if customer asked to talk to a human or requested a meeting handoff"
        }

        memory_context = (
            f"Context Memory: min_budget={memory.budget_min}, max_budget={memory.budget_max}, "
            f"location={memory.preferred_location}, intent={memory.buying_intent}."
        )

        prompt = (
            f"You are NEXOVA AI Sales Employee at {session.organization.name}.\n"
            f"RAG Facts: {rag_context}\n"
            f"Conversation History:\n{history_text}\n"
            f"{memory_context}\n"
            f"Generate response for user message: '{message_content}'"
        )

        try:
            ai_data = AIService.generate_structured_output(prompt, structured_schema)
            reply = ai_data.get("reply", "Thank you for reaching out. A representative will contact you soon.")
            lead_stage = ai_data.get("lead_stage", "CONTACTED")
            budget_min = ai_data.get("budget_min")
            budget_max = ai_data.get("budget_max")
            preferred_location = ai_data.get("preferred_location")
            buying_intent = ai_data.get("buying_intent", "LOW")
            needs_human = ai_data.get("needs_human", False)
        except Exception as e:
            logger.error(f"Error during structured generation: {e}")
            reply = "Thank you. We have received your query and our team will get in touch."
            lead_stage = "CONTACTED"
            budget_min = budget_max = preferred_location = None
            buying_intent = "LOW"
            needs_human = True

        # Save assistant message
        AICustomerChatMessage.objects.create(
            session=session,
            role=AICustomerChatMessage.Roles.ASSISTANT,
            content=reply
        )

        # Update Conversation Memory
        if budget_min is not None:
            memory.budget_min = budget_min
        if budget_max is not None:
            memory.budget_max = budget_max
        if preferred_location:
            memory.preferred_location = preferred_location
        memory.buying_intent = buying_intent
        memory.save()

        # Update conversation status
        old_status = session.status
        if needs_human:
            session.status = AICustomerChatSession.Statuses.WAITING_FOR_AGENT
        else:
            session.status = AICustomerChatSession.Statuses.WAITING_FOR_CUSTOMER
        session.save(update_fields=["status"])

        # 6. Downstream CRM Automation Handoff
        try:
            CRMService.process_qualification_result(
                organization=session.organization,
                customer=session.customer,
                lead_stage=lead_stage,
                buying_intent=buying_intent,
                needs_human=needs_human,
                summary=reply
            )
        except Exception as e:
            logger.error(f"Downstream CRM processing failed: {e}")

        # 7. Asynchronous Event Dispatching for Analytics
        try:
            AnalyticsDispatcher.dispatch_event(
                organization=session.organization,
                campaign=session.campaign,
                event_type="reply",
                details={
                    "customer_id": session.customer.id,
                    "intent": detected_intent,
                    "buying_intent": buying_intent,
                    "needs_human": needs_human
                }
            )
        except Exception as e:
            logger.error(f"Analytics dispatching failed: {e}")

        return {
            "reply": reply,
            "state_changed": old_status != session.status,
            "needs_human": needs_human
        }
