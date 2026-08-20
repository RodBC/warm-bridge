"""Camoufox + Playwright persistent profile driver."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generator

from ..config import SessionConfig
from .browser_page import PlaywrightBrowserPage
from .rate_limit import RateLimit, polite_sleep

__all__ = [
    "RateLimit",
    "polite_sleep",
    "build_camoufox",
    "quit_browser",
    "launch_persistent",
    "new_page",
]


def _require_camoufox() -> Any:
    try:
        from camoufox.sync_api import Camoufox
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            'Camoufox não instalado. Rode: pip install -e ".[linkedin]"'
        ) from exc
    return Camoufox


def _resolve_profile_dir(cfg: SessionConfig) -> Path:
    raw = (cfg.profile_dir or cfg.user_data_dir or "").strip()
    if not raw:
        raise RuntimeError(
            "Perfil Camoufox não configurado. Rode bash scripts/setup_camoufox_profile.sh "
            "ou defina profile_dir em data/linkedin_session.yaml."
        )
    path = Path(raw)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _default_headless() -> bool:
    raw = os.environ.get("WARM_BRIDGE_CAMOUFOX_HEADLESS", "1").strip().lower()
    return raw not in ("0", "false", "no", "off")


def _resolve_headless(cfg: SessionConfig, headless: bool | None) -> bool:
    if headless is not None:
        use_headless = headless
    elif _default_headless():
        use_headless = True
    else:
        use_headless = bool(cfg.headless)
    if os.environ.get("WARM_BRIDGE_SESSION_HEADED", "").strip() in ("1", "true", "yes"):
        use_headless = False
    return use_headless


@dataclass
class CamoufoxSession:
    """Holds Camoufox context manager, browser, and page."""

    cm: Any
    browser: Any
    page: Any
    browser_page: PlaywrightBrowserPage

    def quit(self) -> None:
        quit_browser(self)


@contextmanager
def launch_persistent(
    cfg: SessionConfig,
    *,
    headless: bool | None = None,
) -> Generator[Any, None, None]:
    """Persistent Camoufox context (cookies under profile_dir). Yields BrowserContext."""
    Camoufox = _require_camoufox()
    profile_path = _resolve_profile_dir(cfg)
    use_headless = _resolve_headless(cfg, headless)
    kwargs: dict[str, Any] = {
        "headless": use_headless,
        "humanize": True,
        "persistent_context": True,
        "user_data_dir": str(profile_path),
        "geoip": True,
    }
    try:
        with Camoufox(**kwargs) as context:
            yield context
    except RuntimeError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(
            f"Could not start Camoufox profile ({exc}). "
            "Warm session: warm-bridge burner-login"
        ) from exc


def new_page(browser_or_context: Any) -> Any:
    """Get a page from Browser or persistent BrowserContext."""
    pages = getattr(browser_or_context, "pages", None)
    if pages:
        return pages[0]
    return browser_or_context.new_page()


def build_camoufox(cfg: SessionConfig, *, headless: bool | None = None) -> CamoufoxSession:
    """Launch Camoufox with persistent profile; headless + humanize by default."""
    Camoufox = _require_camoufox()
    profile_path = _resolve_profile_dir(cfg)
    use_headless = _resolve_headless(cfg, headless)

    cm = Camoufox(
        persistent_context=True,
        user_data_dir=str(profile_path),
        headless=use_headless,
        humanize=True,
        geoip=True,
    )
    browser = cm.__enter__()
    page = new_page(browser)
    return CamoufoxSession(
        cm=cm,
        browser=browser,
        page=page,
        browser_page=PlaywrightBrowserPage(page),
    )


def quit_browser(session: CamoufoxSession | Any) -> None:
    try:
        if isinstance(session, CamoufoxSession):
            session.cm.__exit__(None, None, None)
        elif hasattr(session, "quit"):
            session.quit()
    except Exception:  # noqa: BLE001
        pass
