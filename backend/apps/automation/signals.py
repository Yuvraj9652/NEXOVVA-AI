from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def seed_default_data(sender, **kwargs):
    """Hook for app-specific post-migration initialization."""
    return None
