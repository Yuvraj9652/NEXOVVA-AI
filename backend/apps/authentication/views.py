import uuid

from django.conf import settings
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.models import Site
from django.http import HttpResponseBadRequest
from django.urls import reverse
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.google.provider import GoogleProvider
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.authentication.serializers import (
    RegisterSerializer,
    LoginSerializer,
    ProfileSerializer,
    ProfileUpdateSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    VerifyEmailSerializer,
    VerifyOTPSerializer,
    VerifyResetOTPSerializer,
    ResendVerificationSerializer,
    ResendOTPSerializer,
)
from apps.authentication.services import AuthService, ProfileService


class RegisterView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    @extend_schema(
        summary="Initiate register",
        description="Creates a temporary PendingRegistration record and emails verification OTP.",
        responses={
            200: OpenApiResponse(description="Registration OTP sent successfully")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.register(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Registration initiated. Verification OTP sent to email.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyOTPSerializer
    throttle_scope = "otp"

    @extend_schema(
        summary="Verify email registration OTP",
        description="Creates the main User profile and returns JWT tokens upon correct OTP input.",
        responses={
            200: OpenApiResponse(description="Email verified, User registered successfully")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.verify_otp(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "OTP verified successfully. User registered.",
                "data": result,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class ResendOTPView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResendOTPSerializer
    throttle_scope = "otp"

    @extend_schema(
        summary="Resend registration verification OTP",
        description="Resends a new 6-digit OTP code, enforcing 60-second cooldown and 3-resend limits.",
        responses={
            200: OpenApiResponse(description="OTP resent successfully")
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.resend_otp(serializer.validated_data["email"])
        return Response(
            {
                "success": True,
                "message": "New OTP dispatched to email.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class LoginView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer
    throttle_scope = "login"

    @extend_schema(
        summary="Login user",
        description="Authenticates credentials (Username or Email) and returns JWT access & refresh tokens.",
        responses={
            200: OpenApiResponse(
                description="Login successful"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = AuthService.login(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Login successful.",
                "data": result,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        summary="Logout user",
        description="Blacklists the user's refresh token.",
        request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
        responses={
            200: OpenApiResponse(description="Logout successful")
        }
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                    "data": {},
                    "errors": [{"code": "required", "field": "refresh", "message": "This field is required."}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        AuthService.logout(refresh_token)
        return Response(
            {
                "success": True,
                "message": "Logout successful.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Refresh access token",
        description="Rotates access (and optionally refresh) tokens.",
        request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
        responses={
            200: OpenApiResponse(description="Token refresh successful")
        }
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {
                    "success": False,
                    "message": "Refresh token is required.",
                    "data": {},
                    "errors": [{"code": "required", "field": "refresh", "message": "This field is required."}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        result = AuthService.refresh(refresh_token)
        return Response(
            {
                "success": True,
                "message": "Token refreshed successfully.",
                "data": result,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class ProfileView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProfileUpdateSerializer
        return ProfileSerializer

    @extend_schema(
        summary="Retrieve user profile",
        description="Fetches current user's profile and metadata.",
        responses={200: ProfileSerializer}
    )
    def get(self, request, *args, **kwargs):
        profile = ProfileService.get_profile(request.user)
        serializer = ProfileSerializer(profile)
        return Response(
            {
                "success": True,
                "message": "Profile retrieved successfully.",
                "data": serializer.data,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update user profile",
        description="Updates profile and custom user details.",
        responses={200: ProfileSerializer}
    )
    def patch(self, request, *args, **kwargs):
        profile = ProfileService.get_profile(request.user)
        serializer = ProfileUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_profile = ProfileService.update_profile(request.user, serializer.validated_data)
        result = ProfileSerializer(updated_profile).data
        return Response(
            {
                "success": True,
                "message": "Profile updated successfully.",
                "data": result,
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    @extend_schema(
        summary="Change password",
        description="Changes the password of the currently authenticated user.",
        responses={200: OpenApiResponse(description="Password changed successfully")}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.change_password(request.user, serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Password changed successfully.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class ForgotPasswordView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ForgotPasswordSerializer
    throttle_scope = "otp"

    @extend_schema(
        summary="Request password reset OTP",
        description="Generates a password reset 6-digit OTP and emails it to the user.",
        responses={200: OpenApiResponse(description="Instructions sent successfully")}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.forgot_password(serializer.validated_data["email"])
        return Response(
            {
                "success": True,
                "message": "Password reset OTP dispatched.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class VerifyResetOTPView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = VerifyResetOTPSerializer
    throttle_scope = "otp"

    @extend_schema(
        summary="Verify password reset OTP",
        description="Validates that the password reset OTP matches.",
        responses={200: OpenApiResponse(description="OTP matches successfully")}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.verify_reset_otp(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Password reset OTP is valid.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer
    throttle_scope = "otp"

    @extend_schema(
        summary="Confirm password reset with OTP",
        description="Resets the password using a valid email, new password, and 6-digit reset OTP.",
        responses={200: OpenApiResponse(description="Password reset successful")}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        AuthService.reset_password(serializer.validated_data)
        return Response(
            {
                "success": True,
                "message": "Password has been successfully reset.",
                "data": {},
                "errors": [],
            },
            status=status.HTTP_200_OK,
        )


# Legacy verify view to prevent imports failures
class VerifyEmailView(VerifyOTPView):
    pass


# Legacy resend view to prevent imports failures
class ResendVerificationView(ResendOTPView):
    pass


class GoogleLoginRedirectView(View):
    def get(self, request, *args, **kwargs):
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            site = Site.objects.order_by("id").first()

        app = SocialApp.objects.filter(provider="google", sites=site).first()
        if not app:
            app = SocialApp.objects.filter(provider="google").first()

        if not app:
            import os
            client_id = os.getenv("GOOGLE_CLIENT_ID", "dummy-google-client-id")
            secret = os.getenv("GOOGLE_CLIENT_SECRET", "dummy-google-client-secret")
            if client_id and secret and client_id != "dummy-google-client-id":
                app, _ = SocialApp.objects.get_or_create(
                    provider="google",
                    defaults={
                        "name": "Google",
                        "client_id": client_id,
                        "secret": secret,
                        "key": "",
                    },
                )
                app.sites.add(site)

        if not app:
            return HttpResponseBadRequest("Google OAuth is not configured for this site.")

        if site and site not in app.sites.all():
            app.sites.add(site)

        provider = GoogleProvider(request, app=app)
        adapter = GoogleOAuth2Adapter(request)
        client = adapter.get_client(request, app)

        backend_url = getattr(settings, "BACKEND_URL", None)
        if backend_url and "testserver" not in request.get_host():
            callback_url = f"{backend_url.rstrip('/')}{reverse('google_login_callback')}"
        else:
            callback_url = request.build_absolute_uri(reverse("google_login_callback"))
        client.callback_url = callback_url

        scope = provider.get_scope()
        auth_params = provider.get_auth_params_from_request(request, "authenticate")
        state = str(uuid.uuid4())
        client.state = state

        redirect_url = client.get_redirect_url(
            adapter.authorize_url,
            scope,
            auth_params,
        )
        return redirect(redirect_url)


class GoogleLoginSuccessView(View):
    def get(self, request, *args, **kwargs):
        code = request.GET.get("code")
        state = request.GET.get("state")
        if not code:
            frontend_base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
            return redirect(f"{frontend_base_url}/login?error=oauth_cancelled")

        app = SocialApp.objects.filter(provider="google").first()
        if not app:
            frontend_base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
            return redirect(f"{frontend_base_url}/login?error=oauth_not_configured")

        adapter = GoogleOAuth2Adapter(request)
        client = adapter.get_client(request, app)
        client.state = state

        backend_url = getattr(settings, "BACKEND_URL", None)
        if backend_url and "testserver" not in request.get_host():
            callback_url = f"{backend_url.rstrip('/')}{reverse('google_login_callback')}"
        else:
            callback_url = request.build_absolute_uri(reverse("google_login_callback"))
        client.callback_url = callback_url

        try:
            access_token_data = client.get_access_token(code)
            token = adapter.parse_token(access_token_data)
            if app.pk:
                token.app = app
            social_login = adapter.complete_login(request, app, token, response=access_token_data)
            social_login.token = token
            if state:
                social_login.state = {"state_id": state}
            complete_social_login(request, social_login)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("Google OAuth Error:", repr(e))
            if settings.DEBUG:
                raise
            frontend_base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
            return redirect(f"{frontend_base_url}/login?error=oauth_failed")

        user = social_login.user
        tokens = AuthService.handle_social_login(user)

        frontend_base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000").rstrip("/")
        frontend_url = f"{frontend_base_url}/oauth-callback?access={tokens['access']}&refresh={tokens['refresh']}"
        return redirect(frontend_url)
