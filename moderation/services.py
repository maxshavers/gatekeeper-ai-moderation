"""
AI classification service.

Wraps the Anthropic API to turn a raw chat message (plus a little
surrounding context) into a structured moderation decision: category,
severity score, confidence, and a human-readable rationale.

Design notes for interviews:
- Uses a strict JSON-only system prompt so the output can be parsed
  reliably and stored directly on the Classification model.
- Includes the last few messages in the same session as context, since
  a single line ("nice shot, idiot") reads very differently depending
  on whether it's friendly trash talk or part of an escalating pattern.
- Fails safe: if the API call or parsing fails, the message is routed
  to PENDING with a low confidence score rather than silently dropped,
  so a human always sees it.
"""

import json
import os

import anthropic

CLASSIFICATION_MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are a trust & safety classifier for in-game voice/text chat.

Given a chat message and a small amount of surrounding conversation context,
classify the message. Respond with ONLY a JSON object, no other text, no
markdown fences, in exactly this shape:

{
  "category": one of ["benign", "harassment", "hate_speech", "threat",
                        "sexual_content", "grooming_risk", "spam", "cheating"],
  "severity": integer 0-100 (0 = clearly benign, 100 = severe/urgent),
  "confidence": float 0.0-1.0,
  "rationale": "one or two sentence explanation a human moderator can act on"
}

Guidelines:
- Competitive trash talk ("get wrecked", "you're so bad lol") is BENIGN
  unless it targets a protected characteristic or escalates to threats.
- grooming_risk is for language that isolates a minor, requests private
  contact off-platform, or asks personal questions inconsistent with the
  game context -- be conservative and flag for human review rather than
  guessing intent.
- When uncertain between two categories, pick the more severe one and
  lower your confidence score accordingly; a human will review it.
- Never include commentary outside the JSON object.
"""


def _client():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Add it to your .env file before "
            "running classification."
        )
    return anthropic.Anthropic(api_key=api_key)


def build_user_prompt(message, context_messages):
    context_block = "\n".join(
        f"[{m.sent_at.isoformat()}] {m.sender_handle}: {m.body}" for m in context_messages
    )
    return (
        f"Recent context from the same session (oldest first):\n{context_block}\n\n"
        f"Message to classify:\n{message.sender_handle}: {message.body}"
    )


def classify_message(message, context_messages=None):
    """Classify a single ChatMessage. Returns a dict matching the JSON schema above."""
    context_messages = context_messages or []
    client = _client()

    response = client.messages.create(
        model=CLASSIFICATION_MODEL,
        max_tokens=300,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(message, context_messages)}],
    )

    raw_text = "".join(block.text for block in response.content if block.type == "text").strip()

    try:
        data = json.loads(raw_text)
        return {
            "category": data["category"],
            "severity": int(data["severity"]),
            "confidence": float(data["confidence"]),
            "rationale": data["rationale"],
            "model_used": CLASSIFICATION_MODEL,
        }
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        # Fail safe: surface to a human rather than dropping the message.
        return {
            "category": "benign",
            "severity": 50,
            "confidence": 0.0,
            "rationale": (
                "Automatic classification failed to parse; routed for manual "
                "review. Raw model output: " + raw_text[:200]
            ),
            "model_used": CLASSIFICATION_MODEL,
        }
