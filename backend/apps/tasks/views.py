from rest_framework import viewsets, permissions
from apps.tasks.serializers import TasksSerializer
from apps.tasks.selectors import TasksSelector
from apps.tasks.services import TasksService
from apps.authentication.permissions import IsOrganizationMember


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TasksSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]

    def get_queryset(self):
        completed_param = self.request.query_params.get("completed")
        completed = None
        if completed_param is not None:
            completed = completed_param.lower() in ["true", "1", "yes"]

        assigned_to_id = self.request.query_params.get("assigned_to")

        return TasksSelector.list_tasks(
            organization=self.request.organization,
            completed=completed,
            assigned_to_id=assigned_to_id,
        )

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        assigned_to = validated_data.pop("assigned_to", None)
        contact = validated_data.pop("contact", None)
        deal = validated_data.pop("deal", None)
        lead = validated_data.pop("lead", None)

        task = TasksService.create_task(
            organization=self.request.organization,
            user=self.request.user,
            assigned_to_id=assigned_to.id if assigned_to else None,
            contact_id=contact.id if contact else None,
            deal_id=deal.id if deal else None,
            lead_id=lead.id if lead else None,
            **validated_data,
        )
        serializer.instance = task

    def perform_update(self, serializer):
        validated_data = serializer.validated_data

        assigned_to_id = None
        if "assigned_to" in validated_data:
            assigned_to = validated_data.pop("assigned_to")
            assigned_to_id = assigned_to.id if assigned_to else None
        elif self.get_object().assigned_to:
            assigned_to_id = self.get_object().assigned_to.id

        contact_id = None
        if "contact" in validated_data:
            contact = validated_data.pop("contact")
            contact_id = contact.id if contact else None
        elif self.get_object().contact:
            contact_id = self.get_object().contact.id

        deal_id = None
        if "deal" in validated_data:
            deal = validated_data.pop("deal")
            deal_id = deal.id if deal else None
        elif self.get_object().deal:
            deal_id = self.get_object().deal.id

        lead_id = None
        if "lead" in validated_data:
            lead = validated_data.pop("lead")
            lead_id = lead.id if lead else None
        elif self.get_object().lead:
            lead_id = self.get_object().lead.id

        task = TasksService.update_task(
            organization=self.request.organization,
            user=self.request.user,
            task_id=self.get_object().id,
            assigned_to_id=assigned_to_id,
            contact_id=contact_id,
            deal_id=deal_id,
            lead_id=lead_id,
            **validated_data,
        )
        serializer.instance = task

    def perform_destroy(self, instance):
        TasksService.delete_task(
            organization=self.request.organization,
            user=self.request.user,
            task_id=instance.id,
        )
