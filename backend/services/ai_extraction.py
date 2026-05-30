"""Modular AI extraction layer.

Active provider: Gemini (via Emergent LLM key / emergentintegrations).
Future provider: Claude (Anthropic) — placeholder ready, same JSON schema.

Select provider with AI_PROVIDER env var ("gemini" by default).
API keys live in the backend only and are never returned to the frontend.
"""
import json
import logging
import os
import re
import uuid

from fields import FIELD_NAMES, NOT_FOUND_EVIDENCE

logger = logging.getLogger("ai_extraction")

GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")

MAX_TEXT_CHARS = 30000  # keep prompt within sane bounds

SYSTEM_PROMPT = (
    "You are a meticulous real-estate lease abstraction assistant. "
    "You extract a fixed set of fields from the lease text provided and return "
    "STRICT JSON ONLY. You never invent values. You only use the text provided."
)


def _build_prompt(lease_text: str) -> str:
    fields_list = "\n".join(f"- {name}" for name in FIELD_NAMES)
    return f"""Extract ONLY the following lease abstraction fields from the lease text below.

FIELDS TO EXTRACT (use these exact fieldName values):
{fields_list}

RULES:
- Return strict JSON only. Do NOT include markdown, code fences, or commentary.
- Do not guess. Do not invent values. Use ONLY the lease text provided.
- If a field is not explicitly found: value="", confidence=0, evidence="{NOT_FOUND_EVIDENCE}", status="missing".
- If a field is found but unclear/ambiguous: status="needs_review".
- For extracted values, include a short evidence snippet (verbatim) from the lease text.
- confidence is a number between 0 and 1.

Return EXACTLY this JSON schema:
{{
  "fileName": "",
  "summary": "<2-3 sentence neutral summary of the lease>",
  "overallStatus": "processed | needs_review | failed",
  "fields": [
    {{
      "fieldName": "",
      "value": "",
      "confidence": 0,
      "evidence": "",
      "status": "extracted | missing | needs_review"
    }}
  ]
}}

LEASE TEXT:
\"\"\"
{lease_text[:MAX_TEXT_CHARS]}
\"\"\"
"""


def _strip_json(raw: str) -> str:
    """Best-effort extraction of a JSON object from a model response."""
    raw = raw.strip()
    # remove ```json ... ``` fences if present
    raw = re.sub(r"^```[a-zA-Z]*", "", raw).strip()
    raw = re.sub(r"```$", "", raw).strip()
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start:end + 1]
    return raw


def _failed_payload(reason: str) -> dict:
    return {
        "summary": reason,
        "overallStatus": "needs_review",
        "fields": [],  # normalized to all-missing downstream
    }


async def _gemini_extract(lease_text: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    chat = LlmChat(
        api_key=api_key,
        session_id=f"lease-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model("gemini", GEMINI_MODEL)

    response = await chat.send_message(UserMessage(text=_build_prompt(lease_text)))
    return _parse_response(str(response), provider="gemini", text_len=len(lease_text))


async def _claude_extract(lease_text: str) -> dict:
    """Placeholder for future Claude (Anthropic) extraction.

    When Anthropic access is available:
      - read ANTHROPIC_API_KEY from environment
      - call Claude Sonnet from the backend
      - send the lease text, request strict JSON only
      - use the SAME JSON schema as Gemini
    Gemini remains the active provider for now.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("EMERGENT_LLM_KEY")
    if not api_key:
        raise RuntimeError("Anthropic/Claude API key is not configured.")

    from emergentintegrations.llm.chat import LlmChat, UserMessage

    chat = LlmChat(
        api_key=api_key,
        session_id=f"lease-{uuid.uuid4()}",
        system_message=SYSTEM_PROMPT,
    ).with_model("anthropic", "claude-sonnet-4-6")

    response = await chat.send_message(UserMessage(text=_build_prompt(lease_text)))
    return _parse_response(str(response), provider="claude", text_len=len(lease_text))


def _parse_response(raw: str, provider: str, text_len: int) -> dict:
    try:
        data = json.loads(_strip_json(raw))
        if not isinstance(data, dict):
            raise ValueError("Top-level JSON is not an object")
        fields = data.get("fields") or []
        logger.info(
            "AI extraction OK | provider=%s text_len=%d fields_returned=%d",
            provider, text_len, len(fields),
        )
        return {
            "summary": data.get("summary", ""),
            "overallStatus": data.get("overallStatus", "needs_review"),
            "fields": fields,
        }
    except Exception as e:
        logger.warning(
            "AI extraction returned invalid JSON | provider=%s text_len=%d err=%s",
            provider, text_len, e,
        )
        return _failed_payload("AI returned an unpar. Marked for manual review.")


PROVIDERS = {
    "gemini": _gemini_extract,
    "claude": _claude_extract,
}


async def extract_fields(lease_text: str) -> dict:
    """Main entry point. Returns {summary, overallStatus, fields} (raw, un-normalized).

    Never raises for model/parse errors — returns a needs_review payload instead,
    so a bad document never crashes the app.
    """
    provider = os.environ.get("AI_PROVIDER", "gemini").lower()
    fn = PROVIDERS.get(provider, _gemini_extract)

    if not lease_text or not lease_text.strip():
        return _failed_payload("No text could be extracted from this document.")

    try:
        return await fn(lease_text)
    except RuntimeError:
        # configuration error (missing key) — surface to caller
        raise
    except Exception as e:
        logger.warning("AI provider '%s' failed: %s", provider, e)
        return _failed_payload("AI extraction failed. Marked for manual review.")
