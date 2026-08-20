"""Detect LinkedIn login / 2FA challenge screens (thin shim).

Bootstrap owns the full Career Fit challenge state machine.
This module keeps URL/DOM helpers for any non-bootstrap callers.
"""

from __future__ import annotations

from typing import Any, Literal

from ..burner.bootstrap import authed_url, detect_challenge_from_text

ChallengeType = Literal[
    "none",
    "email_otp",
    "totp",
    "app",
    "sms",
    "captcha",
    "bad_creds",
    "password",
    "unknown",
]


def is_logged_in(page: Any) -> bool:
    """URL-based auth probe (preferred over fragile DOM heuristics)."""
    try:
        raw = getattr(page, "_page", page)
        current = getattr(raw, "url", "") or ""
        if authed_url(current):
            return True
    except Exception:  # noqa: BLE001
        pass
    return False


def detect_challenge(page: Any) -> ChallengeType:
    """Return challenge type from visible DOM text + URL."""
    if is_logged_in(page):
        return "none"

    url = ""
    try:
        raw = getattr(page, "_page", page)
        url = getattr(raw, "url", "") or ""
    except Exception:  # noqa: BLE001
        pass

    body = _page_text(page)
    kind = detect_challenge_from_text(url=url, body=body)
    # Back-compat alias for older callers expecting "app"
    if kind == "totp":
        return "app"
    if kind in ("email_otp", "sms", "captcha", "bad_creds", "none"):
        return kind  # type: ignore[return-value]
    if "password" in body.lower() or "senha" in body.lower():
        return "password"
    if any(h in (url or "").lower() for h in ("/login", "/checkpoint", "/uas/login")):
        return "password"
    return "unknown"


def _page_text(page: Any) -> str:
    try:
        raw_page = getattr(page, "_page", None)
        if raw_page is not None:
            return raw_page.inner_text("body") or ""
    except Exception:  # noqa: BLE001
        pass
    try:
        els = page.find_elements("css selector", "body")
        if els:
            return els[0].text or ""
    except Exception:  # noqa: BLE001
        pass
    return ""


def wait_for_login_or_challenge(
    page: Any,
    *,
    timeout_sec: float = 90,
    poll_sec: float = 1.0,
) -> ChallengeType:
    """Poll until logged in or a challenge is detected."""
    import time

    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        kind = detect_challenge(page)
        if kind in ("none", "email_otp", "app", "sms", "password", "captcha", "bad_creds"):
            return kind
        time.sleep(poll_sec)
    return "unknown"
