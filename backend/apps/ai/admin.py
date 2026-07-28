from django.contrib import admin
from .models import PromptTemplate, AIChatSession, AIChatMessage, AIUsage

admin.site.register(PromptTemplate)
admin.site.register(AIChatSession)
admin.site.register(AIChatMessage)
admin.site.register(AIUsage)