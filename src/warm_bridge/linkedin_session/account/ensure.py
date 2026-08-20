"""Auto-ensure LinkedIn session is logged in (credentials from data/secrets/)."""

from __future__ import annotations

import os
import threading
import time
from typing import Any

from ..burner.bootstrap import authed_url, bootstrap_account_session
from ..burner.secrets import account_secrets_path, account_secrets_present, load_account_secrets
from ..config import load_session_config
from ..driver.camoufox import launch_persistent, new_page

_lock = threading.Lock()
_last_bootstrap: dict[str, Any] | None = None


def _headed_bootstrap() -> bool:
    return os.environ.get("WARM_BRIDGE_SESSION_HEADED", "").strip() in ("1", "true", "yes")


def probe_session_logged_in(*, headless: bool = True) -> bool:
    """URL-based auth probe after visiting /feed/ (Career Fit pattern)."""
    cfg = load_session_config()
    if not (cfg.profile_dir or cfg.user_data_dir):
        return False
    try:
        with launch_persistent(cfg, headless=headless) as context:
            page = new_page(context)
            page.goto(
                "https://www.linkedin.com/feed/",
                wait_until="domcontentloaded",
                timeout=60_000,
            )
            time.sleep(1.5)
            return authed_url(page.url or "")
    except Exception:  # noqa: BLE001
        return False


def ensure_session_logged_in(
    *,
    force: bool = False,
    headed: bool | None = None,
    timeout_sec: float = 120,
) -> dict[str, Any]:
    """Headless by default. Founder only pastes credentials — agent writes secrets."""
    global _last_bootstrap

    if os.environ.get("WARM_BRIDGE_SKIP_SESSION_BOOT", "").strip() in ("1", "true", "yes"):
        return {"status": "skipped", "reason": "WARM_BRIDGE_SKIP_SESSION_BOOT"}

    if not account_secrets_present():
        return {"status": "no_secrets", "path": "data/secrets/linkedin_account.yaml"}

    with _lock:
        if not force and _last_bootstrap and _last_bootstrap.get("status") == "logged_in":
            return dict(_last_bootstrap)

        use_headed = _headed_bootstrap() if headed is None else headed
        if not force and probe_session_logged_in(headless=not use_headed):
            _last_bootstrap = {"status": "logged_in", "source": "existing_profile"}
            return dict(_last_bootstrap)

        result = bootstrap_account_session(
            secrets=load_account_secrets(),
            headed=use_headed,
            timeout_sec=timeout_sec,
        )
        _last_bootstrap = dict(result)
        return result


def account_public_config() -> dict[str, Any]:
    if not account_secrets_present():
        return {
            "configured": False,
            "path": str(account_secrets_path() or "data/secrets/linkedin_account.yaml"),
        }
    try:
        sec = load_account_secrets()
        return {
            "configured": True,
            "email": sec.email,
            "linkedin_url": sec.linkedin_url,
            "has_gmail_app_password": bool(sec.gmail_app_password),
            "has_gmail_otp": bool(sec.gmail_app_password or sec.gmail_credentials_json),
            "has_totp": bool(sec.totp_secret),
            "profile_dir": sec.profile_dir or load_session_config().profile_dir,
        }
    except Exception as exc:  # noqa: BLE001
        return {"configured": False, "error": str(exc)}
