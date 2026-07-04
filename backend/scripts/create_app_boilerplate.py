from pathlib import Path

root = Path(__file__).resolve().parent.parent / "apps"
root.mkdir(exist_ok=True)
(root / "__init__.py").write_text("", encoding="utf-8")

apps = [
    "accounts",
    "authentication",
    "organizations",
    "crm",
    "contacts",
    "companies",
    "leads",
    "pipeline",
    "tasks",
    "calendar",
    "communications",
    "notes",
    "documents",
    "notifications",
    "dashboard",
    "analytics",
    "ai",
    "automation",
    "integrations",
    "billing",
    "subscriptions",
    "reports",
    "settings_app",
    "audit",
    "api",
    "common",
]

for app_name in apps:
    app_dir = root / app_name
    app_dir.mkdir(exist_ok=True)
    (app_dir / "__init__.py").write_text("", encoding="utf-8")

    class_name = "".join(part.capitalize() for part in app_name.split("_"))
    label = app_name.replace("_", " ").title()

    (app_dir / "apps.py").write_text(
        f"from django.apps import AppConfig\n\n\nclass {class_name}Config(AppConfig):\n"
        '    default_auto_field = "django.db.models.BigAutoField"\n'
        f'    name = "apps.{app_name}"\n'
        f'    verbose_name = "{label}"\n',
        encoding="utf-8",
    )
    (app_dir / "admin.py").write_text("from django.contrib import admin\n\n\n# Register your models here.\n", encoding="utf-8")
    (app_dir / "models.py").write_text("from django.db import models\n\n\n# Create your models here.\n", encoding="utf-8")
    (app_dir / "views.py").write_text(
        "from django.http import JsonResponse\n\n\ndef health_check(request):\n    return JsonResponse({\"status\": \"ok\"})\n",
        encoding="utf-8",
    )
    (app_dir / "serializers.py").write_text(
        f"from rest_framework import serializers\n\n\nclass {class_name}Serializer(serializers.Serializer):\n"
        '    """Base serializer placeholder for future API models."""\n\n'
        "    pass\n",
        encoding="utf-8",
    )
    (app_dir / "permissions.py").write_text(
        "from rest_framework.permissions import BasePermission\n\n\n"
        f"class {class_name}Permission(BasePermission):\n"
        f'    """Placeholder permission for {label} app."""\n\n'
        "    def has_permission(self, request, view):\n"
        "        return True\n",
        encoding="utf-8",
    )
    (app_dir / "urls.py").write_text("from django.urls import path\n\n\nurlpatterns = []\n", encoding="utf-8")
    (app_dir / "services.py").write_text(
        f"class {class_name}Service:\n"
        f'    """Service layer for {label} app."""\n\n'
        "    pass\n",
        encoding="utf-8",
    )
    (app_dir / "selectors.py").write_text(
        f"class {class_name}Selector:\n"
        f'    """Selector layer for {label} app."""\n\n'
        "    pass\n",
        encoding="utf-8",
    )
    (app_dir / "repositories.py").write_text(
        f"class {class_name}Repository:\n"
        f'    """Repository layer for {label} app."""\n\n'
        "    pass\n",
        encoding="utf-8",
    )
    (app_dir / "signals.py").write_text(
        "from django.db.models.signals import post_migrate\n"
        "from django.dispatch import receiver\n\n\n"
        "@receiver(post_migrate)\n"
        "def seed_default_data(sender, **kwargs):\n"
        '    """Hook for app-specific post-migration initialization."""\n'
        "    return None\n",
        encoding="utf-8",
    )
    (app_dir / "tests.py").write_text(
        "from django.test import TestCase\n\n\n"
        f"class {class_name}Tests(TestCase):\n"
        "    def test_placeholder(self):\n"
        "        self.assertTrue(True)\n",
        encoding="utf-8",
    )
