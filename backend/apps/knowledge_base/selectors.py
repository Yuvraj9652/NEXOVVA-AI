from django.db import models
from apps.properties.models import Project


class ProjectSelector:
    @staticmethod
    def list_projects(organization, status=None, property_type=None, city=None, builder=None, search=None):
        queryset = Project.objects.filter(organization=organization)
        if status:
            queryset = queryset.filter(status=status)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        if city:
            queryset = queryset.filter(city__icontains=city)
        if builder:
            queryset = queryset.filter(builder__icontains=builder)
        if search:
            queryset = queryset.filter(
                models.Q(name__icontains=search)
                | models.Q(builder__icontains=search)
                | models.Q(city__icontains=search)
                | models.Q(rera_number__icontains=search)
                | models.Q(address__icontains=search)
            )
        return queryset

    @staticmethod
    def get_project(organization, project_id):
        return Project.objects.filter(organization=organization, id=project_id).first()

    @staticmethod
    def get_project_with_related(organization, project_id):
        return Project.objects.filter(organization=organization, id=project_id).prefetch_related(
            "media", "kb_documents", "amenities", "versions", "tags", "faqs", "highlights", "processing_jobs"
        ).first()
