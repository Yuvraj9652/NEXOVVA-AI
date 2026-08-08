from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.common.models import TenantModel


class PromptTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    template = models.TextField()
    purpose = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


import uuid


class AIChatSession(TenantModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default="New Conversation")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_chat_sessions")
    status = models.CharField(max_length=20, default="ACTIVE")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title


class AIChatMessage(models.Model):
    class Roles(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(AIChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Roles.choices)
    content = models.TextField()
    metadata = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"



class AIUsage(TenantModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_usages")
    model_name = models.CharField(max_length=100)
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.model_name} - ${self.cost}"


class AICustomerChatSession(TenantModel):
    class Statuses(models.TextChoices):
        NEW = "NEW", "New"
        ACTIVE = "ACTIVE", "Active"
        WAITING_FOR_CUSTOMER = "WAITING_FOR_CUSTOMER", "Waiting for Customer"
        WAITING_FOR_AI = "WAITING_FOR_AI", "Waiting for AI"
        WAITING_FOR_AGENT = "WAITING_FOR_AGENT", "Waiting for Agent" # Human handoff
        MEETING_BOOKED = "MEETING_BOOKED", "Meeting Booked"
        CLOSED = "CLOSED", "Closed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey("customers.Customer", on_delete=models.CASCADE, related_name="ai_sessions")
    status = models.CharField(max_length=30, choices=Statuses.choices, default=Statuses.NEW)
    project = models.ForeignKey("properties.Project", on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_ai_sessions")
    campaign = models.ForeignKey("broadcast.Campaign", on_delete=models.SET_NULL, null=True, blank=True, related_name="customer_ai_sessions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"Chat Session for {self.customer.first_name} {self.customer.last_name} ({self.status})"

    def save(self, *args, **kwargs):
        if self.customer and self.customer.organization_id != self.organization_id:
            raise ValidationError("Customer must belong to the same organization as the chat session.")
        super().save(*args, **kwargs)


class AICustomerChatMessage(models.Model):
    class Roles(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(AICustomerChatSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=20, choices=Roles.choices)
    content = models.TextField()
    metadata = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"


class AIChatMemory(TenantModel):
    session = models.OneToOneField(AICustomerChatSession, on_delete=models.CASCADE, related_name="memory")
    budget_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    preferred_location = models.CharField(max_length=255, blank=True, default="")
    buying_intent = models.CharField(max_length=50, default="LOW")
    extracted_entities = models.JSONField(default=dict, blank=True)
    last_summary = models.TextField(blank=True, default="")
    salesperson_assigned = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_chat_memories")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "AI Chat Memories"

    def __str__(self):
        return f"Memory for session {self.session.id}"

