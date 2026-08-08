from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.conf import settings
from apps.accounts.models import Profile, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profiles(sender, instance, created,raw=False, **kwargs):
    """Automatically create Profile and UserProfile when a User is created."""
    if raw:
        return
    if created:
        Profile.objects.get_or_create(user=instance)
        from apps.organizations.models import Organization
        default_org, _ = Organization.objects.get_or_create(name="Default Organization")
        UserProfile.objects.get_or_create(user=instance, defaults={"organization": default_org})


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profiles(sender, instance,raw=False, **kwargs):
    """Save the profiles when the User is saved."""
    if raw:
        return
    if hasattr(instance, "profile"):
        instance.profile.save()
    if hasattr(instance, "userprofile"):
        instance.userprofile.save()


@receiver(post_migrate)
def seed_default_data(sender, **kwargs):
    """Hook for app-specific post-migration initialization."""
    return None
