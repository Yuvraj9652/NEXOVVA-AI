from apps.tasks.models import Task


class CalendarService:
    @staticmethod
    def get_events(organization):
        return Task.objects.filter(
            organization=organization
        ).values(
            "id",
            "title",
            "due_date",
            "completed",
        )