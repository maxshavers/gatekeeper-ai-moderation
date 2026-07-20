from rest_framework import serializers

from .models import ChatMessage, Classification, ModeratorAction


class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = [
            "id", "category", "severity", "confidence", "rationale",
            "model_used", "status", "created_at",
        ]


class ChatMessageSerializer(serializers.ModelSerializer):
    classifications = ClassificationSerializer(many=True, read_only=True)

    class Meta:
        model = ChatMessage
        fields = [
            "id", "game_session_id", "sender_handle", "body", "sent_at",
            "created_at", "classifications",
        ]


class ModeratorActionSerializer(serializers.ModelSerializer):
    moderator_username = serializers.CharField(source="moderator.username", read_only=True, default=None)

    class Meta:
        model = ModeratorAction
        fields = [
            "id", "classification", "moderator_username", "previous_status",
            "new_status", "note", "created_at",
        ]
