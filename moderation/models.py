from django.db import models
from django.contrib.auth.models import User


class ChatMessage(models.Model):
    """A single in-game chat message pulled into the moderation pipeline."""

    game_session_id = models.CharField(max_length=64, help_text="Match/lobby identifier")
    sender_handle = models.CharField(max_length=64)
    body = models.TextField()
    sent_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.sender_handle}: {self.body[:40]}"

    @property
    def latest_classification(self):
        return self.classifications.order_by("-created_at").first()


class Classification(models.Model):
    """AI-generated classification of a single ChatMessage."""

    class Category(models.TextChoices):
        BENIGN = "benign", "Benign"
        HARASSMENT = "harassment", "Harassment / Bullying"
        HATE_SPEECH = "hate_speech", "Hate Speech"
        THREAT = "threat", "Threat of Violence"
        SEXUAL_CONTENT = "sexual_content", "Sexual Content"
        GROOMING_RISK = "grooming_risk", "Grooming-Risk Language"
        SPAM = "spam", "Spam / Advertising"
        CHEATING = "cheating", "Cheating / Exploit Discussion"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        APPROVED = "approved", "Cleared"
        WARNED = "warned", "Warning Issued"
        MUTED = "muted", "Muted"
        BANNED = "banned", "Banned"

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name="classifications")
    category = models.CharField(max_length=32, choices=Category.choices)
    severity = models.PositiveSmallIntegerField(help_text="0 (benign) - 100 (severe)")
    rationale = models.TextField(help_text="Model-generated explanation for the classification")
    confidence = models.FloatField(help_text="0.0 - 1.0 model confidence", default=0.0)
    model_used = models.CharField(max_length=64, default="claude-sonnet-4-6")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-severity", "-created_at"]

    def __str__(self):
        return f"{self.category} ({self.severity}) - {self.message_id}"


class ModeratorAction(models.Model):
    """Audit-logged record of a human decision on a classification.

    Mirrors the audit-trail pattern (user, timestamp, field-level change)
    used in the Community Impact Dashboard, applied here to moderation
    decisions instead of financial records.
    """

    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, related_name="actions")
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    previous_status = models.CharField(max_length=16)
    new_status = models.CharField(max_length=16)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.previous_status} -> {self.new_status} by {self.moderator}"
