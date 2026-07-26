from apps.accounts.models import UserProfile


class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.organization = None
        request.user_profile = None

        print("=" * 60)
        print("TenantMiddleware")
        print("Authenticated:", request.user.is_authenticated)
        print("User:", request.user)

        if request.user and request.user.is_authenticated:
            try:
                profile = UserProfile.objects.select_related("organization").get(
                    user=request.user
                )

                print("Profile:", profile)
                print("Organization:", profile.organization)

                request.user_profile = profile
                request.organization = profile.organization

            except UserProfile.DoesNotExist:
                print("UserProfile DOES NOT EXIST")

        response = self.get_response(request)
        return response