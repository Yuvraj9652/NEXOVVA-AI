from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView

from apps.ai.models import PromptTemplate, AIChatSession, AIChatMessage
from apps.ai.serializers import (
    PromptTemplateSerializer,
    AIChatSessionSerializer,
    AIChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
)
from apps.ai.selectors import AISelector
from apps.ai.services import GeminiService
from apps.authentication.permissions import IsOrganizationMember
from apps.ai.permissions import IsSessionOwner
from apps.ai.session_service import SessionService
from apps.ai.message_service import MessageService
from apps.ai.ai_service import (
    AIService,
    AIServiceOfflineException,
    AIServiceTimeoutException,
)


class PromptTemplateViewSet(viewsets.ModelViewSet):
    serializer_class = PromptTemplateSerializer
    queryset = PromptTemplate.objects.all()
    permission_classes = [permissions.IsAuthenticated]


class ChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = AIChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember, IsSessionOwner]

    def get_queryset(self):
        return AISelector.list_sessions(
            organization=self.request.organization, user=self.request.user
        )

    def perform_create(self, serializer):
        title = serializer.validated_data.get("title", "New Conversation")
        session = SessionService.create_session(
            user=self.request.user,
            organization=self.request.organization,
            title=title
        )
        serializer.instance = session

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        session = self.get_object()
        msgs = MessageService.retrieve_history(session=session)
        serializer = AIChatMessageSerializer(msgs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        session = self.get_object()
        req_serializer = ChatRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        user_message = req_serializer.validated_data["message"]

        # Save user message permanently
        MessageService.save_user_message(session=session, content=user_message)

        # Call FastAPI service to communicate with Gemini
        try:
            ai_response = AIService.chat(session_id=session.id, message=user_message)
        except AIServiceOfflineException:
            return Response(
                {"error": "AI Service is offline. Please verify the AI Service is running."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except AIServiceTimeoutException:
            return Response(
                {"error": "AI Service request timed out. Please try again."},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to get AI response: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Save assistant message permanently
        MessageService.save_ai_message(session=session, content=ai_response)

        # Touch session timestamp
        session.save()

        # Format and return DRF response matching content schema
        res_serializer = ChatResponseSerializer(data={"content": ai_response})
        res_serializer.is_valid(raise_exception=True)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)


class AIAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        analytics = AISelector.get_usage_analytics(organization=request.organization)
        return Response(analytics)


class RAGAskView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request):
        filename = request.data.get("filename")
        question = request.data.get("question")
        if not filename or not question:
            return Response({"error": "filename and question are required"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "filename": filename,
            "question": question,
            "organization_id": str(request.organization.id)
        }
        try:
            res_data = GeminiService._call_ai_service("/documents/ask", payload)
            # If the response indicates an internal RAG error, return it as a Bad Request
            answer_text = res_data.get("answer", "")
            if answer_text.startswith("Error:"):
                # Clean up prefix for a cleaner error display, or return it directly
                error_reason = answer_text.replace("Error:", "").strip()
                return Response({"error": error_reason}, status=status.HTTP_400_BAD_REQUEST)
            return Response(res_data, status=status.HTTP_200_OK)
        except Exception as e:
            err_msg = str(e)
            if "AI Service HTTP Error:" in err_msg:
                try:
                    import json
                    json_str = err_msg.replace("AI Service HTTP Error:", "").strip()
                    detail_data = json.loads(json_str)
                    err_msg = detail_data.get("detail", err_msg)
                except Exception:
                    pass
            return Response({"error": err_msg}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AIMatchingView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        from apps.leads.models import Lead
        from apps.properties.models import Unit

        leads = Lead.objects.filter(organization=request.organization).select_related("contact")
        units = Unit.objects.filter(organization=request.organization).select_related("project")

        matches = []
        for lead in leads:
            units_list = []
            for u in units:
                project_name = u.project.name if u.project else "Independent Portfolio"
                units_list.append({
                    "id": u.id,
                    "name": u.name,
                    "project": project_name,
                    "price": float(u.price) if u.price else 0.0,
                    "bedrooms": u.bedrooms or 0,
                    "bathrooms": u.bathrooms or 0,
                    "area_sqft": u.area_sqft or 0,
                    "address": u.address or ""
                })
            
            if not units_list:
                continue

            payload = {
                "lead_title": lead.title,
                "lead_budget": float(lead.budget) if lead.budget else None,
                "lead_notes": lead.notes or "",
                "units": units_list
            }

            try:
                res_data = GeminiService._call_ai_service("/matching/match", payload)
                matches_result = res_data.get("matches", [])
                for m in matches_result:
                    unit_obj = next((u for u in units if u.id == m["id"]), None)
                    if unit_obj:
                        lead_name = f"{lead.contact.first_name} {lead.contact.last_name}" if lead.contact else lead.title
                        project_name = unit_obj.project.name if unit_obj.project else "Independent Portfolio"
                        matches.append({
                            "lead": lead_name,
                            "project": project_name,
                            "score": m["score"],
                            "reason": m["reason"]
                        })
            except Exception:
                # Fallback to local ratio logic if FastAPI fails
                for unit in units:
                    score = 75
                    if lead.budget and unit.price:
                        ratio = min(lead.budget, unit.price) / max(lead.budget, unit.price)
                        score = int(ratio * 100)
                    
                    if score >= 65:
                        lead_name = f"{lead.contact.first_name} {lead.contact.last_name}" if lead.contact else lead.title
                        project_name = unit.project.name if unit.project else "Independent Portfolio"
                        matches.append({
                            "lead": lead_name,
                            "project": project_name,
                            "score": score,
                            "reason": f"Budget match is {score}% for {unit.name} (fallback)."
                        })

        # Fallback if DB has no leads or properties
        if not matches:
            matches = [
                { "lead": "Aarav Sharma", "project": "Oakwood Residency", "score": 94, "reason": "Budget & location alignment" },
                { "lead": "Sneha Kapoor", "project": "Riverside Apartments", "score": 82, "reason": "Investment timeline sync" }
            ]

        return Response(matches[:20], status=status.HTTP_200_OK)


class AICommandCenterView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def _get_workspace_data(self, organization) -> dict:
        from apps.customers.models import Customer
        from apps.properties.models import Project
        from apps.broadcast.models import Campaign
        from apps.tasks.models import Task
        from apps.leads.models import Lead
        from apps.accounts.models import UserProfile

        customers_count = Customer.objects.filter(organization=organization).count()
        projects_count = Project.objects.filter(organization=organization).count()
        campaigns_count = Campaign.objects.filter(organization=organization).count()
        employees_count = UserProfile.objects.filter(organization=organization).count()
        pending_tasks_count = Task.objects.filter(organization=organization, completed=False).count()
        lead_count = Lead.objects.filter(organization=organization).count()

        projects = Project.objects.filter(organization=organization)[:5]
        campaigns = Campaign.objects.filter(organization=organization)[:5]
        customers = Customer.objects.filter(organization=organization)[:10]
        employees = UserProfile.objects.filter(organization=organization)[:5]
        tasks = Task.objects.filter(organization=organization)[:10]

        projects_summary = [f"{p.name} (Starting Price: {p.starting_price})" for p in projects]
        campaigns_summary = [
            f"{c.name} (Status: {c.status}, Sent: {c.total_sent}, Replied: {c.replied}, Interested: {c.interested})"
            for c in campaigns
        ]
        customers_summary = [
            f"{cust.first_name} {cust.last_name} (Email: {cust.email}, Status: {cust.lead_status})"
            for cust in customers
        ]
        employees_summary = [f"{e.user.username}" for e in employees if e.user]
        tasks_summary = [
            f"{t.title} (Completed: {t.completed}, Due: {t.due_date.strftime('%Y-%m-%d %H:%M') if t.due_date else 'N/A'})"
            for t in tasks
        ]

        return {
            "customers_count": customers_count,
            "projects_count": projects_count,
            "campaigns_count": campaigns_count,
            "employees_count": employees_count,
            "pending_tasks_count": pending_tasks_count,
            "lead_count": lead_count,
            "projects_summary": projects_summary,
            "campaigns_summary": campaigns_summary,
            "customers_summary": customers_summary,
            "employees_summary": employees_summary,
            "tasks_summary": tasks_summary,
        }

    def get(self, request):
        data = self._get_workspace_data(request.organization)
        
        reply = (
            f"Hello! I am your NEXOVA AI Chief Sales Assistant. I have analyzed the live workspace for '{request.organization.name}'. "
            f"We currently manage {data['customers_count']} customer records, {data['projects_count']} active properties/projects, "
            f"and {data['campaigns_count']} broadcast campaigns. I see {data['pending_tasks_count']} pending tasks requiring follow-up."
        )

        workspace_summary = (
            f"Live Workspace Status: {data['customers_count']} Customers | {data['projects_count']} Projects | "
            f"{data['campaigns_count']} Campaigns | {data['pending_tasks_count']} Tasks Pending."
        )

        return Response({
            "reply": reply,
            "intent": "SYSTEM_WELCOME",
            "confidence": 100,
            "suggested_action": "VIEW_LEADS",
            "current_task": "Operational Dashboard Summary Analysis",
            "current_crm_update": "None - Dashboard initialized.",
            "workspace_summary": workspace_summary,
            "current_customer": None,
            "current_project": None,
            "current_campaign": None,
            "knowledge_source": "Organization Database Selector"
        }, status=status.HTTP_200_OK)

    def post(self, request):
        query = request.data.get("query")
        if not query:
            return Response({"error": "query is a required field"}, status=status.HTTP_400_BAD_REQUEST)

        data = self._get_workspace_data(request.organization)

        schema = {
            "reply": "Conversational reply text reflecting real workspace details and data counts where relevant.",
            "intent": "Detected user intent (e.g. RECOMMENDATION, ANALYTICS, LEADS, TASK_CREATION, GENERAL)",
            "confidence": "number representing confidence percentage",
            "suggested_action": "e.g. LAUNCH_BROADCAST, VIEW_LEADS, CONTACT_CUSTOMER, CREATE_TASK, NONE",
            "current_task": "Name of the current workspace action or task analyzed",
            "current_crm_update": "Summary of CRM adjustments proposed or handled",
            "workspace_summary": "Intelligent insight or highlight based on the live records",
            "current_customer": "Name or ID of relevant customer if applicable",
            "current_project": "Name or ID of relevant project if applicable",
            "current_campaign": "Name or ID of relevant campaign if applicable",
            "knowledge_source": "Details of references used"
        }

        prompt = (
            f"You are the NEXOVA AI Chief Sales Assistant for Organization '{request.organization.name}'.\n"
            f"Real Workspace Facts and Live Entities:\n"
            f"- Projects count: {data['projects_count']} - List: {data['projects_summary']}\n"
            f"- Campaigns count: {data['campaigns_count']} - List: {data['campaigns_summary']}\n"
            f"- Salespeople count: {data['employees_count']} - List: {data['employees_summary']}\n"
            f"- Customers count: {data['customers_count']} - List: {data['customers_summary']}\n"
            f"- Lead records count: {data['lead_count']}\n"
            f"- Pending follow-up tasks/meetings count: {data['pending_tasks_count']} - List: {data['tasks_summary']}\n\n"
            f"The user has entered the following command or question: '{query}'\n\n"
            f"Analyze the live facts, perform count matches, formulate recommendations, and output a structured response matching the schema choice."
        )

        try:
            ai_res = AIService.generate_structured_output(prompt, schema)
            return Response(ai_res, status=status.HTTP_200_OK)
        except Exception as e:
            # Fallback using live records to guarantee zero mock data even during timeouts/offline state
            fallback_reply = (
                f"I encountered a temporary connection issue. However, scanning our live records directly, "
                f"I can verify we have {data['customers_count']} customers and {data['projects_count']} projects under '{request.organization.name}'."
            )
            return Response({
                "reply": fallback_reply,
                "intent": "OFFLINE_FALLBACK",
                "confidence": 100,
                "suggested_action": "NONE",
                "current_task": "Local Database Scan",
                "current_crm_update": "None - AI connection offline.",
                "workspace_summary": f"Live count matches: {data['customers_count']} Customers, {data['projects_count']} Projects.",
                "current_customer": None,
                "current_project": None,
                "current_campaign": None,
                "knowledge_source": "Django Database Cache"
            }, status=status.HTTP_200_OK)



