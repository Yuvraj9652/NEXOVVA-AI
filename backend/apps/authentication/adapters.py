from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """
        Invoked before the social login is completed.
        If a user with this email already exists in our database, we automatically
        connect the social account to that user rather than failing or redirecting.
        """
        # If the social account is already linked to a user, do nothing
        if sociallogin.is_existing:
            return

        email = sociallogin.user.email
        if not email:
            return

        User = get_user_model()
        try:
            # Check for a user with the same email
            user = User.objects.get(email__iexact=email)
            # Connect the social account to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass
