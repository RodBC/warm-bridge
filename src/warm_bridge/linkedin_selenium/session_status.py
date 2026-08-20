"""LinkedIn session readiness — structured blockers for API/UI (no scrape)."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from ..models import ROOT
from .config import load_session_config


def _mock_mode() -> bool:
    return os.environ.get("WARM_BRIDGE_SELENIUM_MOCK", "").strip().lower() in (
        "1",
        "true",
        "yes",
    )


def _selenium_importable() -> tuple[bool, str]:
    try:
        import selenium  # noqa: F401

        return True, getattr(selenium, "__version__", "ok")
    except ImportError:
        return False, ""


def _resolve_chrome_binary(configured: str) -> tuple[str | None, list[str]]:
    """Return (path or None, candidates tried)."""
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


def session_status() -> dict[str, Any]:
    """Return `{ready, blockers[], hints[], checks}` for live Mapear.

    `ready` means a real (non-mock) Chrome session path can be attempted.
    Mock mode is reported but does not count as live-ready.
    """
    cfg = load_session_config()
    session_yaml = ROOT / "data" / "linkedin_session.yaml"
    default_profile = ROOT / "data" / "chrome_profile"

    selenium_ok, selenium_ver = _selenium_importable()
    chrome_path, chrome_tried = _resolve_chrome_binary(cfg.chrome_binary)

    user_data = (cfg.user_data_dir or "").strip()
    if not user_data and default_profile.exists():
        user_data = str(default_profile)
    user_data_path = Path(user_data) if user_data else None
    user_data_exists = bool(user_data_path and user_data_path.is_dir())

    mock = _mock_mode()
    yaml_present = session_yaml.is_file()

    checks: dict[str, Any] = {
        "selenium_importable": selenium_ok,
        "selenium_version": selenium_ver or None,
        "chrome_binary": chrome_path,
        "chrome_binary_configured": bool(cfg.chrome_binary.strip()),
        "user_data_dir": user_data or None,
        "user_data_dir_exists": user_data_exists,
        "linkedin_session_yaml": yaml_present,
        "linkedin_session_yaml_path": str(session_yaml) if yaml_present else None,
        "mock_mode": mock,
        "profile_directory": cfg.profile_directory or None,
    }

    blockers: list[str] = []
    hints: list[str] = []

    if mock:
        hints.append(
            "WARM_BRIDGE_SELENIUM_MOCK=1 — Mapear usa fixture offline, não a sessão Chrome."
        )

    if not selenium_ok:
        blockers.append("selenium_missing")
        hints.append('Instale: pip install -e ".[linkedin]" (no .venv-wb).')

    if not chrome_path:
        blockers.append("chrome_missing")
        hints.append(
            "Instale Linux Chrome no WSL: "
            "sudo apt-get update && sudo apt-get install -y google-chrome-stable"
        )
        hints.append(
            "Windows Chrome não serve para o chromedriver Linux — precisa do binário Linux."
        )
        if chrome_tried:
            hints.append(f"Procurado: {', '.join(chrome_tried)}.")

    if not user_data:
        blockers.append("user_data_dir_missing")
        hints.append("Rode: bash scripts/setup_chrome_profile.sh")
        hints.append(
            "Ou defina user_data_dir em data/linkedin_session.yaml / WARM_BRIDGE_CHROME_USER_DATA."
        )
    elif not user_data_exists:
        blockers.append("user_data_dir_absent")
        hints.append(
            f"Pasta não existe: {user_data}. Rode bash scripts/setup_chrome_profile.sh"
        )
    else:
        # Profile dir exists but may never have logged into LinkedIn — soft hint only.
        hints.append(
            "Abra o Chrome uma vez com esse perfil e faça login no LinkedIn antes de Mapear."
        )

    if not yaml_present and user_data_exists:
        hints.append(
            "Opcional: copie data/linkedin_session.yaml.example → data/linkedin_session.yaml"
        )

    hints.append("Guia: docs/LINKEDIN_SELENIUM.md")

    # Live ready = can attempt real driver (mock is separate UX path).
    ready = selenium_ok and bool(chrome_path) and user_data_exists and not mock
    # If mock, still "ready" for offline Mapear? Plan says ready flips after install
    # for live path. Keep ready=false under mock so UI shows yellow.
    if mock and selenium_ok:
        # Yellow: can demo, not live.
        pass

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
    """Map known Chrome/Selenium failures to PT messages pointing at status panel."""
    raw = str(exc)
    low = raw.lower()
    status = 503

    if isinstance(exc, Exception) and getattr(exc, "status", None):
        status = int(getattr(exc, "status"))

    # Already remapped (e.g. service → API double-call).
    if "painel sessão linkedin" in low or "scripts/setup_chrome_profile" in low:
        return raw, status

    if "selenium não instalado" in low or "no module named 'selenium'" in low:
        return (
            "Selenium não instalado. Painel Sessão LinkedIn → "
            'pip install -e ".[linkedin]". Veja /api/linkedin-session/status.',
            503,
        )
    if "chrome" in low and (
        "not found" in low
        or "cannot find" in low
        or "no such file" in low
        or "binary" in low
        or "chrome failed" in low
    ):
        return (
            "Chrome Linux não encontrado. Instale google-chrome-stable no WSL "
            "e confira o painel Sessão LinkedIn (/api/linkedin-session/status).",
            503,
        )
    if "user data directory is already in use" in low or "profile is in use" in low or "lock" in low:
        return (
            "Perfil Chrome bloqueado (outra janela aberta?). Feche o Chrome desse "
            "user-data-dir e tente de novo. Painel Sessão LinkedIn.",
            503,
        )
    if "sessão chrome não configurada" in low or (
        "user_data_dir" in low and "não" in low
    ):
        return (
            "Sessão Chrome não configurada. Rode bash scripts/setup_chrome_profile.sh "
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
