from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from apps.authentication.views import (
    RegisterView,
    CustomTokenObtainPairView,
    UserProfileView,
    EmailVerificationRequestView,
    EmailVerifyConfirmView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("login/", CustomTokenObtainPairView.as_view(), name="auth_login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth_token_refresh"),
    path("me/", UserProfileView.as_view(), name="auth_me"),
    path("verify-email/request/", EmailVerificationRequestView.as_view(), name="auth_verify_email_request"),
    path("verify-email/confirm/", EmailVerifyConfirmView.as_view(), name="auth_verify_email_confirm"),
    path("password-reset/request/", PasswordResetRequestView.as_view(), name="auth_password_reset_request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth_password_reset_confirm"),
]
