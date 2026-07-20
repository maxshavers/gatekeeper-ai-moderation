"""
Runs AI classification over any ChatMessage that doesn't have a
Classification yet. Batches by session so each message gets recent
same-session context, and skips messages that are already classified
so the command is safe to re-run.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q

from moderation.models import ChatMessage, Classification
from moderation.services import classify_message


class Command(BaseCommand):
    help = "Classify all unclassified chat messages using the Claude API."

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Only classify up to N messages (useful for smoke-testing).",
        )

    def handle(self, *args, **options):
        unclassified = (
            ChatMessage.objects.filter(~Q(classifications__isnull=False))
            .order_by("game_session_id", "sent_at")
        )
        if options["limit"]:
            unclassified = unclassified[: options["limit"]]

        total = unclassified.count() if not options["limit"] else len(unclassified)
        self.stdout.write(f"Classifying {total} message(s)...")

        classified = 0
        failed = 0

        for message in unclassified:
            context = list(
                ChatMessage.objects.filter(
                    game_session_id=message.game_session_id, sent_at__lt=message.sent_at
                ).order_by("-sent_at")[:4]
            )[::-1]

            try:
                result = classify_message(message, context_messages=context)
                Classification.objects.create(
                    message=message,
                    category=result["category"],
                    severity=result["severity"],
                    confidence=result["confidence"],
                    rationale=result["rationale"],
                    model_used=result["model_used"],
                )
                classified += 1
                self.stdout.write(
                    f"  [{result['severity']:>3}] {message.sender_handle}: "
                    f"{result['category']} -- {message.body[:50]}"
                )
            except Exception as exc:  # noqa: BLE001 -- surfaced to stdout for the demo
                failed += 1
                self.stderr.write(f"  FAILED on message {message.id}: {exc}")

        self.stdout.write(self.style.SUCCESS(f"Done. Classified: {classified}, Failed: {failed}"))
