from apps.accounts.models import UserProfile


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        class TenantRequest(request.__class__):
            @property
            def organization(self):
                user = self.user
                if not hasattr(self, '_resolved_user') or self._resolved_user != user:
                    self._resolved_user = user
                    self._resolved_organization = None
                    self._resolved_user_profile = None
                    if user and user.is_authenticated:
                        try:
                            profile = UserProfile.objects.select_related("organization").get(user=user)
                            self._resolved_user_profile = profile
                            self._resolved_organization = profile.organization
                        except UserProfile.DoesNotExist:
                            pass
                return self._resolved_organization

            @property
            def user_profile(self):
                # Ensure organization resolution has run for the current user
                _ = self.organization
                return getattr(self, '_resolved_user_profile', None)

        request.__class__ = TenantRequest
        response = self.get_response(request)
        return response