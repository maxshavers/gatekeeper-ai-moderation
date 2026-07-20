"""
Creates classifications for all unclassified messages using simple
keyword rules instead of the Claude API — useful for demoing the
dashboard with zero API cost. Swap to `classify_messages` for real
AI classification once you're ready to use your API key.
"""
import random
from django.core.management.base import BaseCommand
from moderation.models import ChatMessage, Classification

RULES = [
    (["uninstall", "pathetic", "mind your business", "so bad"], "harassment", (45, 65), 0.82),
    (["find you", "watch yourself"], "threat", (85, 97), 0.91),
    (["grade are you", "discord", "don't tell your parents"], "grooming_risk", (80, 95), 0.74),
    (["telegram", "boosts", "cheap"], "spam", (20, 35), 0.88),
    (["aimbot", "exploit"], "cheating", (55, 70), 0.80),
    (["redacted group"], "hate_speech", (88, 99), 0.90),
]

class Command(BaseCommand):
    help = "Create demo classifications using keyword rules (no API calls, no cost)."

    def handle(self, *args, **options):
        created = 0
        for m in ChatMessage.objects.filter(classifications__isnull=True):
            text = m.body.lower()
            match = next((r for r in RULES if any(k in text for k in r[0])), None)
            if match:
                _, cat, (lo, hi), conf = match
                sev = random.randint(lo, hi)
            else:
                cat, sev, conf = "benign", random.randint(0, 15), 0.95
            Classification.objects.create(
                message=m, category=cat, severity=sev, confidence=conf,
                rationale=f"Demo rule-based classification ({cat}) — no API call made.",
                model_used="demo-rules-v1",
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"Created {created} demo classifications (no API cost)."))