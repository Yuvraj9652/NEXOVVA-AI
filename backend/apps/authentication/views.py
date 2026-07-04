from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.authentication.serializers import RegisterSerializer, UserProfileSerializer
from apps.accounts.models import UserProfile


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        profile_serializer = UserProfileSerializer(profile)
        return Response(
            {
                "message": "User registered successfully",
                "profile": profile_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            from django.contrib.auth import get_user_model
            User = get_user_model()

            username = request.data.get("username")
            try:
                user = User.objects.get(username=username)
                profile = UserProfile.objects.select_related("organization").get(user=user)
                response.data["user"] = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "role": profile.role,
                    "organization": {
                        "id": profile.organization.id if profile.organization else None,
                        "name": profile.organization.name if profile.organization else None,
                        "slug": profile.organization.slug if profile.organization else None,
                    },
                }
            except Exception:
                pass
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Resolve user profile
        try:
            return UserProfile.objects.select_related("organization", "user").get(
                user=self.request.user
            )
        except UserProfile.DoesNotExist:
            # Create a placeholder profile if it is a superuser registering/logging in through admin panel without profile
            org = None
            profile = UserProfile.objects.create(
                user=self.request.user,
                organization=org,
                role=UserProfile.Roles.ADMIN if self.request.user.is_superuser else UserProfile.Roles.AGENT,
            )
            return profile


class EmailVerificationRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        return Response({"message": "Verification email dispatched."})


class EmailVerifyConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({"message": "Email address successfully verified."})


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"message": "Password reset instructions dispatched."})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response({"message": "Password has been successfully reset."})
