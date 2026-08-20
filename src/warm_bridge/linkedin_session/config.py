"""Session config for Camoufox persistent profile (no email/password in API)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models import ROOT


@dataclass
class SessionConfig:
    profile_dir: str = ""
    user_data_dir: str = ""  # legacy alias — maps to profile_dir when set
    profile_directory: str = ""
    backend: str = "camoufox"  # camoufox | selenium
    headless: bool = False
    # Selenium legacy (backend=selenium only)
    chrome_binary: str = ""
    use_webdriver_manager: bool = True
    enrich: bool = True
    enrich_cap: int = 16
    max_mutuals: int = 40


def _default_profile_dir() -> Path:
    return ROOT / "data" / "camoufox_profile"


def load_session_config(override: dict[str, Any] | None = None) -> SessionConfig:
    """Load from env and optional gitignored data/linkedin_session.yaml."""
    data: dict[str, Any] = {}
    cfg_path = ROOT / "data" / "linkedin_session.yaml"
    if cfg_path.exists():
        try:
            import yaml

            loaded = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, dict):
                data.update(loaded)
        except Exception:  # noqa: BLE001
            pass

    env_map = {
        "profile_dir": "WARM_BRIDGE_CAMOUFOX_PROFILE",
        "user_data_dir": "WARM_BRIDGE_CHROME_USER_DATA",
        "profile_directory": "WARM_BRIDGE_CHROME_PROFILE",
        "chrome_binary": "WARM_BRIDGE_CHROME_BINARY",
        "backend": "WARM_BRIDGE_SESSION_BACKEND",
    }
    for key, env in env_map.items():
        val = os.environ.get(env)
        if val:
            data[key] = val

    if override:
        data.update({k: v for k, v in override.items() if v is not None and v != ""})

    profile_dir = str(data.get("profile_dir") or data.get("user_data_dir") or "").strip()
    if not profile_dir and _default_profile_dir().exists():
        profile_dir = str(_default_profile_dir())

    backend = str(data.get("backend") or "camoufox").strip().lower()
    if backend not in ("camoufox", "selenium"):
        backend = "camoufox"

    headless_env = os.environ.get("WARM_BRIDGE_SESSION_HEADLESS", "").strip()
    headless = bool(data.get("headless", False))
    if headless_env in ("1", "true", "yes"):
        headless = True

    enrich_env = os.environ.get("WARM_BRIDGE_SELENIUM_ENRICH")
    enrich = bool(data.get("enrich", True))
    if enrich_env is not None:
        enrich = enrich_env.strip() in ("1", "true", "yes")

    return SessionConfig(
        profile_dir=profile_dir,
        user_data_dir=profile_dir,
        profile_directory=str(data.get("profile_directory") or ""),
        backend=backend,
        headless=headless,
        chrome_binary=str(data.get("chrome_binary") or ""),
        use_webdriver_manager=bool(data.get("use_webdriver_manager", True)),
        enrich=enrich,
        enrich_cap=int(data.get("enrich_cap") or 16),
        max_mutuals=int(data.get("max_mutuals") or 40),
    )


def ensure_data_gitignore_paths() -> list[Path]:
    """Paths that must stay out of git (documented; .gitignore owns enforcement)."""
    return [
        ROOT / "data" / "linkedin_session.yaml",
        ROOT / "data" / "camoufox_profile",
        ROOT / "data" / "chrome_profile",
        ROOT / "data" / "secrets",
    ]
