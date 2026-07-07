from django.contrib import admin
from .models import PromptTemplate, ChatSession, ChatMessage, AIUsage

admin.site.register(PromptTemplate)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(AIUsage)