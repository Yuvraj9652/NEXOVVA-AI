from django.db import transaction
from apps.properties.models import Project
from apps.knowledge_base.models import (
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
from apps.knowledge_base.selectors import ProjectSelector
from decimal import Decimal
from datetime import date, datetime


def _make_json_safe(data):
    if isinstance(data, dict):
        return {k: _make_json_safe(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [_make_json_safe(v) for v in data]
    elif isinstance(data, Decimal):
        return float(data)
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    return data


class ProjectService:
    @staticmethod
    @transaction.atomic
    def create_project(organization, created_by, **validated_data):
        project = Project.objects.create(
            organization=organization,
            created_by=created_by,
            **validated_data
        )
        ProjectAnalytics.objects.create(organization=organization, project=project)
        ProjectVersion.objects.create(
            organization=organization,
            project=project,
            version_number=1,
            change_summary="Project created",
            changed_fields=["all"],
            snapshot=_make_json_safe(validated_data),
            created_by=created_by,
        )
        return project

    @staticmethod
    @transaction.atomic
    def update_project(organization, project, updated_by, **validated_data):
        changed_fields = []
        for field, value in validated_data.items():
            old_value = getattr(project, field)
            if old_value != value:
                changed_fields.append(field)
                setattr(project, field, value)
        project.save()
        if changed_fields:
            last_version = project.versions.filter(organization=organization).order_by("-version_number").first()
            next_version = (last_version.version_number + 1) if last_version else 1
            ProjectVersion.objects.create(
                organization=organization,
                project=project,
                version_number=next_version,
                change_summary=f"Updated: {', '.join(changed_fields)}",
                changed_fields=changed_fields,
                snapshot=_make_json_safe({field: getattr(project, field) for field in changed_fields}),
                created_by=updated_by,
            )
        return project

    @staticmethod
    @transaction.atomic
    def duplicate_project(organization, project, created_by):
        project.pk = None
        project.id = None
        project.name = f"{project.name} (Copy)"
        project.status = Project.ProjectStatus.DRAFT
        project.save()
        ProjectAnalytics.objects.create(organization=organization, project=project)
        ProjectVersion.objects.create(
            organization=organization,
            project=project,
            version_number=1,
            change_summary="Project duplicated",
            changed_fields=["name", "status"],
            snapshot={"name": project.name, "status": project.status},
            created_by=created_by,
        )
        return project

    @staticmethod
    @transaction.atomic
    def archive_project(organization, project, updated_by):
        project.status = Project.ProjectStatus.ARCHIVED
        project.save()
        last_version = project.versions.filter(organization=organization).order_by("-version_number").first()
        next_version = (last_version.version_number + 1) if last_version else 1
        ProjectVersion.objects.create(
            organization=organization,
            project=project,
            version_number=next_version,
            change_summary="Project archived",
            changed_fields=["status"],
            snapshot={"status": Project.ProjectStatus.ARCHIVED},
            created_by=updated_by,
        )
        return project

    @staticmethod
    @transaction.atomic
    def delete_project(organization, project):
        project.delete()

    @staticmethod
    def create_media(organization, project, **validated_data):
        return ProjectMedia.objects.create(organization=organization, project=project, **validated_data)

    @staticmethod
    def create_document(organization, project, **validated_data):
        return ProjectDocument.objects.create(organization=organization, project=project, **validated_data)

    @staticmethod
    def create_amenity(organization, project, **validated_data):
        return ProjectAmenity.objects.create(organization=organization, project=project, **validated_data)

    @staticmethod
    def create_processing_job(organization, project, job_type):
        return ProjectProcessingJob.objects.create(organization=organization, project=project, job_type=job_type)

    @staticmethod
    def update_processing_job(job, **validated_data):
        for field, value in validated_data.items():
            setattr(job, field, value)
        job.save()
        return job

    @staticmethod
    def create_chat_session(organization, project, created_by, title="New Chat"):
        return ProjectChatSession.objects.create(
            organization=organization, project=project, created_by=created_by, title=title
        )

    @staticmethod
    def save_chat_message(session, role, content, metadata=None):
        return ProjectChatMessage.objects.create(
            session=session, role=role, content=content, metadata=metadata or {}
        )
