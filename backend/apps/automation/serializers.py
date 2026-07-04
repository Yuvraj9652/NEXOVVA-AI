from rest_framework import serializers
from apps.automation.models import AutomationRule


class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = ["id", "name", "trigger_event", "action_type", "action_params", "active"]
        read_only_fields = ["id"]
