import re
from datetime import date
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.accounts.models import Profile, UserProfile
from apps.organizations.models import Organization
from apps.organizations.serializers import OrganizationSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", 
            "phone_number", "is_email_verified", "is_phone_verified", "last_activity"
        ]
        read_only_fields = ["id", "is_email_verified", "is_phone_verified", "last_activity"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "user", "organization", "role", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = [
            "id", "user", "avatar", "bio", "date_of_birth", "gender", 
            "website", "github", "linkedin", "location", "timezone", 
            "language", "theme", "organization", "role", "created_at", "updated_at"
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_organization(self, obj):
        try:
            user_profile = UserProfile.objects.select_related("organization").get(user=obj.user)
            if user_profile.organization:
                return OrganizationSerializer(user_profile.organization).data
        except UserProfile.DoesNotExist:
            pass
        return None

    def get_role(self, obj):
        try:
            user_profile = UserProfile.objects.get(user=obj.user)
            return user_profile.role
        except UserProfile.DoesNotExist:
            pass
        return None


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    first_name = serializers.CharField(max_length=150, required=False, default="")
    last_name = serializers.CharField(max_length=150, required=False, default="")
    phone_number = serializers.CharField(max_length=20, required=False, default="", allow_blank=True)
    organization_name = serializers.CharField(max_length=255)

    def validate_username(self, value):
        from apps.authentication.models import PendingRegistration
        from django.utils import timezone
        PendingRegistration.objects.filter(otp_expires_at__lt=timezone.now()).delete()
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        if PendingRegistration.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A registration with this username is already pending.")
        return value

    def validate_email(self, value):
        from apps.authentication.models import PendingRegistration
        from django.utils import timezone
        PendingRegistration.objects.filter(otp_expires_at__lt=timezone.now()).delete()
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        if PendingRegistration.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A registration with this email is already pending.")
        return value

    def validate_phone_number(self, value):
        if value:
            if not re.match(r"^\+?[0-9\s\-()]+$", value):
                raise serializers.ValidationError("Invalid phone number format.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class ProfileUpdateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)

    class Meta:
        model = Profile
        fields = [
            "first_name", "last_name", "phone_number", "avatar", "bio", 
            "date_of_birth", "gender", "website", "github", "linkedin", 
            "location", "timezone", "language", "theme"
        ]

    def validate_date_of_birth(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        return value

    def validate_avatar(self, value):
        if value:
            if value.size > 5 * 1024 * 1024:
                raise serializers.ValidationError("Avatar image size must be less than 5MB.")
            content_type = getattr(value, "content_type", "")
            if content_type and not content_type.startswith("image/"):
                raise serializers.ValidationError("Avatar must be a valid image file.")
        return value

    def validate_phone_number(self, value):
        if value:
            if not re.match(r"^\+?[0-9\s\-()]+$", value):
                raise serializers.ValidationError("Invalid phone number format.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_new_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "New passwords do not match."})
        if data["old_password"] == data["new_password"]:
            raise serializers.ValidationError({"new_password": "New password cannot be same as old password."})
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm_new_password = serializers.CharField(write_only=True, style={"input_type": "password"})

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, data):
        if data["new_password"] != data["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        return data


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)


class VerifyResetOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
