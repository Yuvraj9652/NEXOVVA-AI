from apps.contacts.models import Contact


class CommunicationService:
    @staticmethod
    def get_summary(organization):
        return {
            "emails_sent": 0,
            "sms_sent": 0,
            "calls_logged": 0,
            "contacts": Contact.objects.filter(
                organization=organization
            ).count(),
        }