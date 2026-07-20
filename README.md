# Gatekeeper — AI Content Moderation Prototype for In Game Chat

A trust & safety prototype that ingests in-game chat, classifies each message
with Claude (category, severity, confidence, rationale), and routes flagged
content into a human-review dashboard with full audit logging of moderator
decisions.

Built as a follow-up to a case study on AI-driven gaming trust and safety.
This turns that research into a working system.

## What it does

1. **Ingests chat messages** grouped by game session (synthetic seed data
   included — no real platform data used).
2. **Classifies each message with Claude**, using a strict JSON-schema
   system prompt and a few messages of same-session context, so a line like
   "get wrecked" is read differently depending on whether it's friendly
   trash talk or part of an escalating pattern.
3. **Surfaces flagged messages in a review queue**, sorted by severity, with
   the model's rationale so moderators aren't just trusting a black box.
4. **Logs every moderator decision** (previous status, new status, who, when)
   — the same audit-trail pattern used in the Community Impact Dashboard
   project, applied here to moderation instead of financial records.
5. **Exposes a REST API** (Django REST Framework) over messages,
   classifications, and the action log.

## Architecture

```
moderation/
  models.py          ChatMessage, Classification, ModeratorAction
  services.py         Claude API wrapper — prompt, JSON parsing, fail-safe handling
  views.py             Dashboard, action-taking, audit history
  api_views.py         DRF viewsets (read-only, for integration/demo purposes)
  management/commands/
    seed_data.py        Synthetic gaming chat across 10 sessions
    classify_messages.py Batch-classifies unclassified messages via Claude
  templates/moderation/ Dashboard UI (dark "signal room" console theme)
```

**Design decisions worth mentioning in an interview:**
- Classification is a separate model from ChatMessage (not a field on it),
  so re-classifying or tracking classifier version history is possible
  without mutating the original message.
- The classifier fails *safe*: if the API call or JSON parsing fails, the
  message still gets a Classification row (low confidence, flagged for
  manual review) instead of silently disappearing from the pipeline.
- `classify_messages` is idempotent — it only processes messages without an
  existing Classification, so it's safe to re-run.
- Session context (last few messages) is passed to the classifier because
  moderation decisions are rarely about a single line in isolation.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env   # then add your ANTHROPIC_API_KEY
python manage.py migrate
python manage.py seed_data
python manage.py classify_messages   # calls the Claude API
python manage.py createsuperuser     # optional, for /admin/
python manage.py runserver
```

Then visit:
- `http://127.0.0.1:8000/` — the review queue
- `http://127.0.0.1:8000/history/` — moderator action log
- `http://127.0.0.1:8000/admin/` — Django admin
- `http://127.0.0.1:8000/api/classifications/` — REST API

## Possible extensions

- Confidence-threshold auto-actions (e.g. auto-mute above severity 95 +
  confidence 0.9, human review below that)
- An appeals flow: contested bans generate a Claude-drafted case summary
  referencing platform policy
- Swap the synthetic seed data for a public toxic-comment dataset reshaped
  into chat-log format, for a larger-scale demo
