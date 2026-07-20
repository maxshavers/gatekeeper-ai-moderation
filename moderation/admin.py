from django.contrib import admin

from .models import ChatMessage, Classification, ModeratorAction


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ("sender_handle", "game_session_id", "body", "sent_at")
    list_filter = ("game_session_id",)
    search_fields = ("sender_handle", "body")


@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ("message", "category", "severity", "confidence", "status", "created_at")
    list_filter = ("category", "status")


@admin.register(ModeratorAction)
class ModeratorActionAdmin(admin.ModelAdmin):
    list_display = ("classification", "moderator", "previous_status", "new_status", "created_at")
