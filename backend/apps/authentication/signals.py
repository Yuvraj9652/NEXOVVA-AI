from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone


@receiver(user_logged_in)
def update_user_last_activity(sender, request, user, **kwargs):
    """Update user's last activity timestamp upon successful login."""
    user.last_activity = timezone.now()
    user.save(update_fields=["last_activity"])


@receiver(post_migrate)
def seed_default_data(sender, **kwargs):
    """Hook for app-specific post-migration initialization."""
    return None


from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import get_user_model

@receiver(pre_social_login)
def link_social_account(sender, request, sociallogin, **kwargs):
    """Auto-link social logins to existing local accounts if emails match."""
    email = sociallogin.user.email
    if not email:
        return
    User = get_user_model()
    try:
        user = User.objects.get(email__iexact=email)
        sociallogin.connect(request, user)
    except User.DoesNotExist:
        pass
