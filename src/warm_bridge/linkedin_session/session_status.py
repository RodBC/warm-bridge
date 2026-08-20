"""LinkedIn session readiness — Camoufox-first blockers for API/UI."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..models import ROOT
from .burner.secrets import burner_secrets_present
from .config import load_session_config


def _mock_mode() -> bool:
    for key in ("WARM_BRIDGE_SESSION_MOCK", "WARM_BRIDGE_SELENIUM_MOCK"):
        if os.environ.get(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


def _camoufox_importable() -> tuple[bool, str]:
    try:
        import camoufox  # noqa: F401

        ver = getattr(camoufox, "__version__", "ok")
        return True, str(ver)
    except ImportError:
        return False, ""


def _selenium_importable() -> tuple[bool, str]:
    try:
        import selenium  # noqa: F401

        return True, getattr(selenium, "__version__", "ok")
    except ImportError:
        return False, ""


def _resolve_chrome_binary(configured: str) -> tuple[str | None, list[str]]:
    tried: list[str] = []
    if configured.strip():
        p = Path(configured.strip())
        tried.append(str(p))
        if p.is_file() and os.access(p, os.X_OK):
            return str(p), tried
    for name in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium"):
        found = shutil.which(name)
        tried.append(name)
        if found:
            return found, tried
    return None, tried


def _logged_in_hint(profile_path: Path | None) -> bool:
    """Cookie/storage files suggest a previously warmed Camoufox profile."""
    if not profile_path or not profile_path.is_dir():
        return False
    cookie_hints = [
        profile_path / "cookies.sqlite",
        profile_path / "cookies.sqlite-wal",
        profile_path / "storage",
        profile_path / "Default" / "cookies.sqlite",
    ]
    return any(p.exists() for p in cookie_hints)


def session_status() -> dict[str, Any]:
    """Return `{ready, blockers[], hints[], checks}` for live Mapear."""
    cfg = load_session_config()
    session_yaml = ROOT / "data" / "linkedin_session.yaml"
    default_profile = ROOT / "data" / "camoufox_profile"
    legacy_profile = ROOT / "data" / "chrome_profile"

    camoufox_ok, camoufox_ver = _camoufox_importable()
    selenium_ok, selenium_ver = _selenium_importable()
    chrome_path, chrome_tried = _resolve_chrome_binary(cfg.chrome_binary)

    profile_dir = (cfg.profile_dir or cfg.user_data_dir or "").strip()
    if not profile_dir and default_profile.exists():
        profile_dir = str(default_profile)
    elif not profile_dir and legacy_profile.exists():
        profile_dir = str(legacy_profile)
    profile_path = Path(profile_dir) if profile_dir else None
    profile_exists = bool(profile_path and profile_path.is_dir())
    logged_in_hint = _logged_in_hint(profile_path)

    mock = _mock_mode()
    yaml_present = session_yaml.is_file()
    backend = cfg.backend if cfg.backend in ("camoufox", "selenium") else "camoufox"
    burner_ready = burner_secrets_present()

    checks: dict[str, Any] = {
        "backend": backend,
        "camoufox_importable": camoufox_ok,
        "camoufox_version": camoufox_ver or None,
        "selenium_importable": selenium_ok,
        "selenium_version": selenium_ver or None,
        "chrome_binary": chrome_path,
        "chrome_binary_configured": bool(cfg.chrome_binary.strip()),
        "profile_dir": profile_dir or None,
        "profile_dir_exists": profile_exists,
        "user_data_dir": profile_dir or None,
        "user_data_dir_exists": profile_exists,
        "logged_in_hint": logged_in_hint,
        "linkedin_session_yaml": yaml_present,
        "linkedin_session_yaml_path": str(session_yaml) if yaml_present else None,
        "mock_mode": mock,
        "profile_directory": cfg.profile_directory or None,
        "burner_secrets_present": burner_ready,
    }

    blockers: list[str] = []
    hints: list[str] = []

    if mock:
        hints.append(
            "WARM_BRIDGE_SESSION_MOCK=1 — Mapear usa fixture offline, não sessão live."
        )

    if backend == "camoufox":
        if not camoufox_ok:
            blockers.append("camoufox_missing")
            hints.append('Instale: pip install -e ".[linkedin]" && python -m camoufox fetch')
        if not profile_dir:
            blockers.append("profile_dir_missing")
            hints.append("Rode: bash scripts/setup_camoufox_profile.sh")
        elif not profile_exists:
            blockers.append("profile_dir_absent")
            hints.append(f"Pasta não existe: {profile_dir}. Rode bash scripts/setup_camoufox_profile.sh")
        elif logged_in_hint:
            hints.append("Perfil Camoufox com cookies — sessão provavelmente aquecida.")
        else:
            hints.append(
                "Perfil frio — cole LinkedIn email + password + Gmail App Password no chat "
                "para o agent rodar burner-login headless."
            )
    else:
        if not selenium_ok:
            blockers.append("selenium_missing")
            hints.append('Instale: pip install -e ".[linkedin]"')
        if not chrome_path:
            blockers.append("chrome_missing")
            hints.append("Instale google-chrome-stable no WSL (backend=selenium legado).")
            if chrome_tried:
                hints.append(f"Procurado: {', '.join(chrome_tried)}.")
        if not profile_dir:
            blockers.append("user_data_dir_missing")
            hints.append("Defina profile_dir em data/linkedin_session.yaml")
        elif not profile_exists:
            blockers.append("user_data_dir_absent")
            hints.append(f"Pasta não existe: {profile_dir}")

    if burner_ready:
        hints.append("Conta em data/secrets/linkedin_account.yaml — login headless automático.")
    else:
        hints.append(
            "Cole no chat: LinkedIn email + password + Gmail App Password — agent grava secrets."
        )

    if not yaml_present and profile_exists:
        hints.append("Opcional: copie data/linkedin_session.yaml.example → data/linkedin_session.yaml")

    hints.append("Guia: docs/LINKEDIN_SESSION.md")

    if backend == "camoufox":
        ready = camoufox_ok and profile_exists and not mock
    else:
        ready = selenium_ok and bool(chrome_path) and profile_exists and not mock

    return {
        "ready": ready,
        "blockers": blockers,
        "hints": hints,
        "checks": checks,
        "severity": (
            "ready"
            if ready
            else ("mock" if mock and not blockers else ("blocked" if blockers else "yellow"))
        ),
    }


def friendly_map_error(exc: BaseException) -> tuple[str, int]:
    """Map known session failures to PT messages."""
    raw = str(exc)
    low = raw.lower()
    status = 503

    if isinstance(exc, Exception) and getattr(exc, "status", None):
        status = int(getattr(exc, "status"))

    if "painel sessão linkedin" in low or "setup_camoufox_profile" in low:
        return raw, status

    if "camoufox não instalado" in low or "no module named 'camoufox'" in low:
        return (
            "Camoufox não instalado. Painel Sessão LinkedIn → "
            'pip install -e ".[linkedin]". Veja /api/linkedin-session/status.',
            503,
        )
    if "selenium não instalado" in low or "no module named 'selenium'" in low:
        return (
            "Selenium não instalado (backend legado). "
            'pip install -e ".[linkedin]". Veja /api/linkedin-session/status.',
            503,
        )
    if "chrome" in low and (
        "not found" in low or "cannot find" in low or "no such file" in low or "binary" in low
    ):
        return (
            "Chrome Linux não encontrado (backend selenium). "
            "Prefira backend=camoufox. Painel Sessão LinkedIn.",
            503,
        )
    if "user data directory is already in use" in low or "profile is in use" in low or "lock" in low:
        return (
            "Perfil bloqueado (outra janela aberta?). Feche Camoufox/Chrome e tente de novo.",
            503,
        )
    if "perfil camoufox não configurado" in low or "sessão chrome não configurada" in low:
        return (
            "Sessão não configurada. Rode bash scripts/setup_camoufox_profile.sh "
            "ou abra o painel Sessão LinkedIn.",
            400,
        )
    if "url linkedin do alvo" in low:
        return (raw, 400)
    return (
        f"Falha ao mapear LinkedIn: {raw}. Confira o painel Sessão LinkedIn "
        "(/api/linkedin-session/status).",
        status,
    )
