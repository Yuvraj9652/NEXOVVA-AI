from django.db.models.signals import post_migrate, post_delete
from django.dispatch import receiver
from apps.documents.models import Document
from apps.documents.tasks import delete_document_vector_task
import os


@receiver(post_migrate)
def seed_default_data(sender, **kwargs):
    """Hook for app-specific post-migration initialization."""
    return None


@receiver(post_delete, sender=Document)
def on_document_delete(sender, instance, **kwargs):
    """Trigger vector store deletion asynchronously when a Document is deleted."""
    filename = os.path.basename(instance.file.name)
    delete_document_vector_task.delay(filename, instance.organization.id)

