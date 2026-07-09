from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import UploadedFile
from apps.accounts.models import Profile, UserProfile

User = get_user_model()


class ProfileService:
    @staticmethod
    def get_profile(user: User) -> Profile:
        """Fetch the Profile associated with a user."""
        profile, _ = Profile.objects.get_or_create(user=user)
        return profile

    @staticmethod
    def update_profile(user: User, data: dict) -> Profile:
        """Update fields on the user's Profile and UserProfile."""
        profile, _ = Profile.objects.get_or_create(user=user)
        user_profile, _ = UserProfile.objects.get_or_create(user=user)

        # Update CustomUser fields if present in update payload
        user_fields_to_update = []
        if "first_name" in data:
            user.first_name = data["first_name"]
            user_fields_to_update.append("first_name")
        if "last_name" in data:
            user.last_name = data["last_name"]
            user_fields_to_update.append("last_name")
        if "phone_number" in data:
            user.phone_number = data["phone_number"]
            user_fields_to_update.append("phone_number")
        if user_fields_to_update:
            user.save(update_fields=user_fields_to_update)

        # Update Profile fields
        profile_fields = [
            "bio", "date_of_birth", "gender", "website", "github", 
            "linkedin", "location", "timezone", "language", "theme"
        ]
        profile_fields_to_update = []
        for field in profile_fields:
            if field in data:
                setattr(profile, field, data[field])
                profile_fields_to_update.append(field)
        if "avatar" in data:
            profile.avatar = data["avatar"]
            profile_fields_to_update.append("avatar")

        if profile_fields_to_update:
            profile.save(update_fields=profile_fields_to_update)

        # Update UserProfile fields (e.g. role)
        if "role" in data:
            user_profile.role = data["role"]
            user_profile.save(update_fields=["role"])

        return profile

    @staticmethod
    def upload_avatar(user: User, avatar_file: UploadedFile) -> Profile:
        """Upload avatar image file to user's Profile."""
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.avatar = avatar_file
        profile.save(update_fields=["avatar"])
        return profile
