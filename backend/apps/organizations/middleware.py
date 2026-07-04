from apps.accounts.models import UserProfile


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.user_profile = None

        if request.user and request.user.is_authenticated:
            try:
                profile = UserProfile.objects.select_related("organization").get(user=request.user)
                request.user_profile = profile
                request.organization = profile.organization
            except UserProfile.DoesNotExist:
                pass

        response = self.get_response(request)
        return response
