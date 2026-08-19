"""Reach / outcome events — validate only; never invent replies or statuses."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

ALLOWED_STATUSES = frozenset(
    {
        "copied",
        "sent",
        "bridge_replied",
        "intro_landed",
        "no_reply",
        "dead",
    }
)

# UI chips map to these product statuses (copied is auto-logged on copy/wa).
CHIP_STATUSES = frozenset({"sent", "bridge_replied", "intro_landed", "no_reply"})


class OutcomeError(ValueError):
    """Invalid reach event payload."""


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_event(raw: dict[str, Any]) -> dict[str, Any]:
    """Validate and normalize a reach event. Client remains source of truth."""
    if not isinstance(raw, dict):
        raise OutcomeError("event must be an object")

    status = (raw.get("status") or "").strip()
    if status not in ALLOWED_STATUSES:
        raise OutcomeError(f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")

    target_name = (raw.get("targetName") or raw.get("target_name") or "").strip()
    if not target_name:
        raise OutcomeError("targetName is required")

    bridge_id = (raw.get("bridgeId") or raw.get("bridge_id") or "").strip()
    if not bridge_id:
        raise OutcomeError("bridgeId is required")

    bridge_name = (raw.get("bridgeName") or raw.get("bridge_name") or "").strip()
    if not bridge_name:
        raise OutcomeError("bridgeName is required")

    note_raw = raw.get("note")
    note: str | None = None
    if note_raw is not None:
        note = str(note_raw).strip() or None
        if note and len(note) > 500:
            raise OutcomeError("note max length is 500")

    account = raw.get("accountCompany") or raw.get("account_company")
    account_company = str(account).strip() if account else None
    if account_company == "":
        account_company = None

    event_id = (raw.get("id") or "").strip() or f"r_{uuid4().hex[:12]}"
    at = (raw.get("at") or "").strip() or _iso_now()

    return {
        "id": event_id,
        "at": at,
        "accountCompany": account_company,
        "targetName": target_name,
        "bridgeId": bridge_id,
        "bridgeName": bridge_name,
        "status": status,
        "note": note,
    }


def validate_events(payload: list[Any] | dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize a list of events or a single event / {events: [...]} envelope."""
    if isinstance(payload, dict) and "events" in payload:
        items = payload["events"]
    elif isinstance(payload, dict) and "status" in payload:
        items = [payload]
    elif isinstance(payload, list):
        items = payload
    else:
        raise OutcomeError("expected event object, list, or {events: [...]}")

    if not isinstance(items, list):
        raise OutcomeError("events must be a list")
    return [normalize_event(item) for item in items]
