from django.urls import path, include
from apps.authentication.views import (
    RegisterView,
    VerifyOTPView,
    ResendOTPView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    ProfileView,
    ChangePasswordView,
    ForgotPasswordView,
    VerifyResetOTPView,
    ResetPasswordView,
    GoogleLoginRedirectView,
    GoogleLoginSuccessView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="auth_register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="auth_verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="auth_resend_otp"),
    path("login/", LoginView.as_view(), name="auth_login"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="auth_token_refresh"),
    path("profile/", ProfileView.as_view(), name="auth_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="auth_change_password"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="auth_forgot_password"),
    path("verify-reset-otp/", VerifyResetOTPView.as_view(), name="auth_verify_reset_otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="auth_reset_password"),
    path("google/login/", GoogleLoginRedirectView.as_view(), name="google_login_redirect"),
    path("google/callback/", GoogleLoginSuccessView.as_view(), name="google_login_callback"),
    path("accounts/", include("allauth.socialaccount.urls")), # allauth social views
]
