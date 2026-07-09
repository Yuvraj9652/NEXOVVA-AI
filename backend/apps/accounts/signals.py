from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.conf import settings
from apps.accounts.models import Profile, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profiles(sender, instance, created, **kwargs):
    """Automatically create Profile and UserProfile when a User is created."""
    if created:
        Profile.objects.get_or_create(user=instance)
        # Create a default UserProfile if not already present
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profiles(sender, instance, **kwargs):
    """Save the profiles when the User is saved."""
    if hasattr(instance, "profile"):
        instance.profile.save()
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


@receiver(post_migrate)
def seed_default_data(sender, **kwargs):
    """Hook for app-specific post-migration initialization."""
    return None
