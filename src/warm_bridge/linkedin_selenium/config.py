"""Session config for local Chrome profile (no email/password in API)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models import ROOT


@dataclass
class SessionConfig:
    user_data_dir: str = ""
    profile_directory: str = ""
    chrome_binary: str = ""
    use_webdriver_manager: bool = True
    enrich: bool = True
    enrich_cap: int = 16
    max_mutuals: int = 40


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
        "user_data_dir": "WARM_BRIDGE_CHROME_USER_DATA",
        "profile_directory": "WARM_BRIDGE_CHROME_PROFILE",
        "chrome_binary": "WARM_BRIDGE_CHROME_BINARY",
    }
    for key, env in env_map.items():
        val = os.environ.get(env)
        if val:
            data[key] = val

    if override:
        data.update({k: v for k, v in override.items() if v is not None and v != ""})

    enrich_env = os.environ.get("WARM_BRIDGE_SELENIUM_ENRICH")
    enrich = bool(data.get("enrich", True))
    if enrich_env is not None:
        enrich = enrich_env.strip() in ("1", "true", "yes")

    return SessionConfig(
        user_data_dir=str(data.get("user_data_dir") or ""),
        profile_directory=str(data.get("profile_directory") or ""),
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
        ROOT / "data" / "chrome_profile",
    ]
