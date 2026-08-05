import csv
import io
import json
from django.http import HttpResponse
from django.db.models import Sum, Count, Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.knowledge_base.models import (
    ProjectCategory,
    ProjectMedia,
    ProjectDocument,
    ProjectAmenity,
    ProjectVersion,
    ProjectAnalytics,
    ProjectTag,
    ProjectFAQ,
    ProjectHighlight,
    ProjectProcessingJob,
    ProjectChatSession,
    ProjectChatMessage,
)
from apps.knowledge_base.serializers import (
    ProjectCategorySerializer,
    ProjectMediaSerializer,
    ProjectDocumentSerializer,
    ProjectAmenitySerializer,
    ProjectVersionSerializer,
    ProjectAnalyticsSerializer,
    ProjectTagSerializer,
    ProjectFAQSerializer,
    ProjectHighlightSerializer,
    ProjectProcessingJobSerializer,
    ProjectChatSessionSerializer,
    ProjectChatMessageSerializer,
)
from apps.knowledge_base.services import ProjectService
from apps.knowledge_base.selectors import ProjectSelector
from apps.knowledge_base.permissions import IsOrganizationMember, IsAdminOrManager
from apps.authentication.permissions import IsOrganizationMember as OrgMember
from apps.properties.models import Project
from apps.properties.serializers import ProjectSerializer
import uuid
import json


class ProjectCategoryViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        return ProjectCategory.objects.filter(organization=self.request.organization)

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        queryset = ProjectSelector.list_projects(
            organization=self.request.organization,
            status=self.request.query_params.get("status"),
            property_type=self.request.query_params.get("property_type"),
            city=self.request.query_params.get("city"),
            builder=self.request.query_params.get("builder"),
            search=self.request.query_params.get("search"),
        )
        sort = self.request.query_params.get("sort")
        if sort == "name_asc":
            queryset = queryset.order_by("name")
        elif sort == "price_desc":
            queryset = queryset.order_by("-starting_price")
        elif sort == "price_asc":
            queryset = queryset.order_by("starting_price")
        elif sort == "possession":
            queryset = queryset.order_by("possession_date")
        else:
            queryset = queryset.order_by("-created_at")
        return queryset

    def perform_create(self, serializer):
        project = ProjectService.create_project(
            organization=self.request.organization,
            created_by=self.request.user,
            **serializer.validated_data
        )
        serializer.instance = project

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        project = self.get_object()
        duplicated = ProjectService.duplicate_project(
            organization=request.organization, project=project, created_by=request.user
        )
        serializer = self.get_serializer(duplicated)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        project = self.get_object()
        archived = ProjectService.archive_project(
            organization=request.organization, project=project, updated_by=request.user
        )
        serializer = self.get_serializer(archived)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def analytics(self, request, pk=None):
        project = self.get_object()
        analytics = getattr(project, "kb_analytics", None)
        if not analytics:
            analytics = ProjectAnalytics.objects.create(
                organization=request.organization, project=project
            )
        serializer = ProjectAnalyticsSerializer(analytics)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def generate_ai(self, request, pk=None):
        project = self.get_object()
        job_type = request.data.get("job_type", "description_generation")
        job = ProjectService.create_processing_job(
            organization=request.organization, project=project, job_type=job_type
        )
        serializer = ProjectProcessingJobSerializer(job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        organization = request.organization
        projects = Project.objects.filter(organization=organization)
        stats = {
            "total": projects.count(),
            "past": projects.filter(status=Project.ProjectStatus.PAST).count(),
            "ongoing": projects.filter(status=Project.ProjectStatus.ONGOING).count(),
            "upcoming": projects.filter(status=Project.ProjectStatus.UPCOMING).count(),
            "draft": projects.filter(status=Project.ProjectStatus.DRAFT).count(),
            "archived": projects.filter(status=Project.ProjectStatus.ARCHIVED).count(),
        }
        return Response(stats)

    @action(detail=True, methods=["post"])
    def chat(self, request, pk=None):
        project = self.get_object()
        message = request.data.get("message", "")
        if not message:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        session = ProjectService.create_chat_session(
            organization=request.organization, project=project, created_by=request.user
        )
        ProjectService.save_chat_message(session=session, role="user", content=message)

        try:
            from apps.ai.ai_service import AIService
            context = {
                "project_name": project.name,
                "builder": project.builder,
                "city": project.city,
                "status": project.status,
                "property_type": project.property_type,
                "starting_price": str(project.starting_price) if project.starting_price else "N/A",
                "max_price": str(project.max_price) if project.max_price else "N/A",
                "configurations": project.configurations,
                "amenities": list(project.amenities.values_list("amenity_type", flat=True)),
                "highlights": list(project.highlights.values_list("text", flat=True)),
                "description": project.short_description or project.description,
                "rera_number": project.rera_number,
                "possession_date": str(project.possession_date) if project.possession_date else "N/A",
            }
            ai_message = AIService.call_project_chat(session_id=str(session.session_id), message=message, context=context)
        except Exception as e:
            ai_message = f"AI Service unavailable. Error: {str(e)}"

        ProjectService.save_chat_message(session=session, role="assistant", content=ai_message)
        return Response({"session_id": str(session.session_id), "response": ai_message})

    @action(detail=False, methods=["post"])
    def bulk_import(self, request):
        organization = request.organization
        files = request.FILES.getlist("files")
        if not files:
            return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        imported = []
        errors = []
        for f in files:
            try:
                doc = ProjectDocument.objects.create(
                    organization=organization,
                    project=None,
                    document_type=ProjectDocument.DocumentType.CSV if f.name.endswith(".csv") else ProjectDocument.DocumentType.OTHER,
                    name=f.name,
                    file=f,
                    file_size=f.size,
                    processed=True,
                )

                if f.name.endswith(".csv"):
                    f.seek(0)
                    content = f.read().decode("utf-8-sig", errors="ignore")
                    reader = csv.DictReader(io.StringIO(content))
                    for row in reader:
                        name = row.get("name") or row.get("Name") or row.get("title") or row.get("Title")
                        if not name:
                            continue

                        starting_price = row.get("starting_price") or row.get("Starting Price") or row.get("price")
                        max_price = row.get("max_price") or row.get("Max Price")
                        try:
                            starting_price = float(starting_price) if starting_price else None
                        except (ValueError, TypeError):
                            starting_price = None
                        try:
                            max_price = float(max_price) if max_price else None
                        except (ValueError, TypeError):
                            max_price = None

                        status_val = (row.get("status") or row.get("Status") or "ONGOING").upper()
                        type_val = (row.get("property_type") or row.get("Property Type") or row.get("type") or "APARTMENT").upper()

                        valid_statuses = [c[0] for c in Project.ProjectStatus.choices]
                        if status_val not in valid_statuses:
                            status_val = "ONGOING"

                        valid_types = [c[0] for c in Project.PropertyType.choices]
                        if type_val not in valid_types:
                            type_val = "APARTMENT"

                        project_data = {
                            "name": name.strip(),
                            "description": row.get("description") or row.get("Description") or "",
                            "short_description": row.get("short_description") or row.get("Short Description") or "",
                            "builder": row.get("builder") or row.get("Builder") or "",
                            "city": row.get("city") or row.get("City") or "",
                            "state": row.get("state") or row.get("State") or "",
                            "address": row.get("address") or row.get("Address") or "",
                            "status": status_val,
                            "property_type": type_val,
                            "starting_price": starting_price,
                            "max_price": max_price,
                            "rera_number": row.get("rera_number") or row.get("RERA Number") or "",
                            "image_url": row.get("image_url") or row.get("Image URL") or "",
                        }

                        proj = ProjectService.create_project(
                            organization=organization,
                            created_by=request.user if request.user.is_authenticated else None,
                            **project_data
                        )
                        if proj.image_url:
                            ProjectMedia.objects.create(
                                organization=organization,
                                project=proj,
                                media_type=ProjectMedia.MediaType.IMAGE,
                                file=proj.image_url,
                                caption=f"{proj.name} Cover Image",
                                is_primary=True,
                            )
                        imported.append({"id": proj.id, "name": proj.name, "filename": f.name})

                elif f.name.endswith(".json"):
                    f.seek(0)
                    data = json.loads(f.read().decode("utf-8", errors="ignore"))
                    items = data if isinstance(data, list) else [data]
                    for row in items:
                        name = row.get("name")
                        if not name:
                            continue
                        proj = ProjectService.create_project(
                            organization=organization,
                            created_by=request.user if request.user.is_authenticated else None,
                            **row
                        )
                        imported.append({"id": proj.id, "name": proj.name, "filename": f.name})
                else:
                    imported.append({"filename": f.name, "document_id": doc.id})

            except Exception as e:
                errors.append({"filename": f.name, "error": str(e)})

        return Response({"imported": imported, "errors": errors}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"])
    def sample_csv(self, request):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="sample_projects.csv"'

        writer = csv.writer(response)
        writer.writerow([
            "name", "builder", "property_type", "status", "city", "state", "address",
            "starting_price", "max_price", "rera_number", "image_url", "description", "short_description"
        ])
        writer.writerow([
            "DLF Cyber Horizon", "DLF Homes", "APARTMENT", "ONGOING", "Gurugram", "Haryana",
            "Golf Course Extension Road, Sector 65", "15000000", "32000000", "HRERA-GGM-2024-890",
            "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop",
            "Ultra luxury 3 & 4 BHK residences with private elevators and sky deck views.",
            "Luxury high-rise apartments in Sector 65 Gurugram."
        ])
        writer.writerow([
            "Prestige Elysian Woods", "Prestige Group", "VILLA", "UPCOMING", "Bengaluru", "Karnataka",
            "Bannerghatta Main Road", "28000000", "55000000", "PRM/KA/RERA/1251/310/PR/240101",
            "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop",
            "Exclusive gated community of 4 & 5 BHK luxury villas surrounded by lush greenery.",
            "Premium villa township near Bannerghatta National Park."
        ])
        writer.writerow([
            "Oberoi Sky City", "Oberoi Realty", "PENTHOUSE", "ONGOING", "Mumbai", "Maharashtra",
            "Borivali East, Western Express Highway", "35000000", "80000000", "P51800001578",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop",
            "Duplex sky penthouses offering 360-degree panoramic skyline and sea views.",
            "Iconic penthouses on Western Express Highway Mumbai."
        ])
        writer.writerow([
            "Godrej Waterfront Commercial", "Godrej Properties", "COMMERCIAL", "DRAFT", "Pune", "Maharashtra",
            "Kharadi IT Park", "9500000", "45000000", "P52100028912",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop",
            "Grade-A commercial office spaces and high-street retail shops in Kharadi.",
            "Prime IT park office spaces in Kharadi Pune."
        ])
        return response

    @action(detail=True, methods=["post"])
    def restore(self, request, pk=None):
        project = get_object_or_404(Project, organization=request.organization, id=pk, status=Project.ProjectStatus.ARCHIVED)
        project.status = Project.ProjectStatus.DRAFT
        project.save()
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def trash(self, request):
        organization = request.organization
        projects = Project.objects.filter(organization=organization, status=Project.ProjectStatus.ARCHIVED)
        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)


class ProjectMediaViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectMediaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectMedia.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectDocumentViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectDocument.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        doc = serializer.save(organization=self.request.organization)
        doc.file_size = doc.file.size if doc.file else 0
        doc.save()
        ProjectService.create_processing_job(
            organization=self.request.organization, project=doc.project, job_type="document_extraction"
        )


class ProjectAmenityViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectAmenitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectAmenity.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectVersionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectVersionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectVersion.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset


class ProjectAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request, project_id=None):
        organization = request.organization
        if project_id:
            analytics = ProjectAnalytics.objects.filter(organization=organization, project_id=project_id).first()
            if not analytics:
                project = Project.objects.filter(organization=organization, id=project_id).first()
                if not project:
                    return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
                analytics = ProjectAnalytics.objects.create(organization=organization, project=project)
            serializer = ProjectAnalyticsSerializer(analytics)
            return Response(serializer.data)

        analytics_qs = ProjectAnalytics.objects.filter(organization=organization)
        serializer = ProjectAnalyticsSerializer(analytics_qs, many=True)
        return Response(serializer.data)


class ProjectTagViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectTagSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectTag.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectFAQViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectFAQSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectFAQ.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectHighlightViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectHighlightSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectHighlight.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization)


class ProjectProcessingJobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProjectProcessingJobSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectProcessingJob.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.order_by("-created_at")


class ProjectChatSessionViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        project_id = self.request.query_params.get("project_id")
        queryset = ProjectChatSession.objects.filter(organization=self.request.organization)
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        return queryset.order_by("-updated_at")

    def perform_create(self, serializer):
        serializer.save(organization=self.request.organization, created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def messages(self, request, pk=None):
        session = self.get_object()
        msgs = ProjectChatMessage.objects.filter(session=session).order_by("created_at")
        serializer = ProjectChatMessageSerializer(msgs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def send_message(self, request, pk=None):
        session = self.get_object()
        content = request.data.get("message", "")
        if not content:
            return Response({"error": "message is required"}, status=status.HTTP_400_BAD_REQUEST)

        ProjectChatMessage.objects.create(session=session, role="user", content=content)
        session.save()

        try:
            project = session.project
            context = {
                "project_name": project.name,
                "builder": project.builder,
                "city": project.city,
                "status": project.status,
                "property_type": project.property_type,
                "starting_price": str(project.starting_price) if project.starting_price else "N/A",
                "max_price": str(project.max_price) if project.max_price else "N/A",
                "configurations": project.configurations,
                "amenities": list(project.amenities.values_list("amenity_type", flat=True)),
                "highlights": list(project.highlights.values_list("text", flat=True)),
                "description": project.short_description or project.description,
            }
            from apps.ai.ai_service import AIService
            ai_response = AIService.call_project_chat(session_id=str(session.session_id), message=content, context=context)
        except Exception as e:
            ai_response = f"AI Service unavailable. Error: {str(e)}"

        ProjectChatMessage.objects.create(session=session, role="assistant", content=ai_response)
        session.save()
        return Response({"response": ai_response})


class ProjectExportView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get(self, request):
        organization = request.organization
        projects = Project.objects.filter(organization=organization)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)


class ProjectAIGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def post(self, request, project_id):
        project = get_object_or_404(Project, organization=request.organization, id=project_id)
        generation_type = request.data.get("type", "description")
        context_data = request.data.get("context", {})

        job = ProjectService.create_processing_job(
            organization=request.organization, project=project, job_type=f"ai_generate_{generation_type}"
        )
        job.status = ProjectProcessingJob.JobStatus.PROCESSING
        job.progress = 10
        job.save()

        try:
            from apps.ai.ai_service import AIService
            payload = {
                "project_name": project.name,
                "builder": project.builder,
                "city": project.city,
                "status": project.status,
                "property_type": project.property_type,
                "starting_price": str(project.starting_price) if project.starting_price else "N/A",
                "max_price": str(project.max_price) if project.max_price else "N/A",
                "configurations": project.configurations,
                "amenities": list(project.amenities.values_list("amenity_type", flat=True)),
                "highlights": list(project.highlights.values_list("text", flat=True)),
                "description": project.short_description or project.description,
                "rera_number": project.rera_number,
                "possession_date": str(project.possession_date) if project.possession_date else "N/A",
                "generation_type": generation_type,
                **context_data,
            }
            result = AIService.call_project_ai_generate(payload=payload)
            job.status = ProjectProcessingJob.JobStatus.COMPLETED
            job.progress = 100
            job.result = result
            job.save()
            return Response({"job_id": job.id, "result": result})
        except Exception as e:
            job.status = ProjectProcessingJob.JobStatus.FAILED
            job.error_message = str(e)
            job.save()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
