"""map_target: seller session + target → observed network dict."""

from __future__ import annotations

import os
from typing import Any

from ..linkedin import normalize_linkedin_url, resolve_target_fields
from .config import SessionConfig, load_session_config
from .normalize import rows_to_network


class SessionMapError(Exception):
    """Driver/session failure — surface as 400/503, never invent contacts."""

    def __init__(self, message: str, *, status: int = 503) -> None:
        super().__init__(message)
        self.status = status


# Backward compat alias
SeleniumMapError = SessionMapError


def _use_mock() -> bool:
    for key in ("WARM_BRIDGE_SESSION_MOCK", "WARM_BRIDGE_SELENIUM_MOCK"):
        if os.environ.get(key, "").strip().lower() in ("1", "true", "yes"):
            return True
    return False


def _run_with_camoufox(cfg: SessionConfig, target_url: str, max_mutuals: int) -> list[dict[str, str]]:
    from .driver.camoufox import RateLimit, build_camoufox, quit_browser
    from .mutuals import fetch_mutuals

    session = build_camoufox(cfg)
    try:
        return fetch_mutuals(
            session.browser_page,
            target_url,
            rate=RateLimit(),
            max_mutuals=max_mutuals,
        )
    finally:
        quit_browser(session)


def _run_with_selenium(cfg: SessionConfig, target_url: str, max_mutuals: int) -> list[dict[str, str]]:
    from ..linkedin_selenium.driver import RateLimit, build_chrome, quit_driver
    from .driver.browser_page import SeleniumBrowserPage
    from .mutuals import fetch_mutuals

    driver = build_chrome(cfg)
    try:
        page = SeleniumBrowserPage(driver)
        return fetch_mutuals(page, target_url, rate=RateLimit(), max_mutuals=max_mutuals)
    finally:
        quit_driver(driver)


def _fetch_mutuals(cfg: SessionConfig, target_url: str) -> tuple[Any, list[dict[str, str]]]:
    """Return (live page handle, rows) for enrich phase."""
    backend = (cfg.backend or "camoufox").lower()
    if backend == "selenium":
        from ..linkedin_selenium.driver import RateLimit, build_chrome
        from .driver.browser_page import SeleniumBrowserPage
        from .mutuals import fetch_mutuals

        driver = build_chrome(cfg)
        page = SeleniumBrowserPage(driver)
        rows = fetch_mutuals(page, target_url, rate=RateLimit(), max_mutuals=cfg.max_mutuals)
        return ("selenium", driver, page), rows

    from .driver.camoufox import RateLimit, build_camoufox
    from .mutuals import fetch_mutuals

    session = build_camoufox(cfg)
    rows = fetch_mutuals(
        session.browser_page,
        target_url,
        rate=RateLimit(),
        max_mutuals=cfg.max_mutuals,
    )
    return ("camoufox", session, session.browser_page), rows


def _cleanup_handle(handle: tuple[Any, ...]) -> None:
    kind = handle[0]
    if kind == "camoufox":
        from .driver.camoufox import quit_browser

        quit_browser(handle[1])
    elif kind == "selenium":
        from ..linkedin_selenium.driver import quit_driver

        quit_driver(handle[1])


def map_target(
    seller_linkedin: str,
    target_fields: dict[str, str],
    session_cfg: SessionConfig | None = None,
    *,
    mock: bool | None = None,
    mock_empty: bool = False,
) -> dict[str, Any]:
    """Return `{network, meta}` from session-observed mutuals (or mock fixture)."""
    cfg = session_cfg or load_session_config()
    fields = resolve_target_fields(
        name=target_fields.get("name") or "",
        company=target_fields.get("company") or "",
        title=target_fields.get("title") or "",
        linkedin=target_fields.get("linkedin_url")
        or target_fields.get("linkedin")
        or target_fields.get("name")
        or "",
    )
    target_name = fields["name"]
    target_url = fields["linkedin_url"] or ""
    seller_url = normalize_linkedin_url(seller_linkedin) or (seller_linkedin or "").strip()

    use_mock = _use_mock() if mock is None else mock
    if use_mock:
        from .mock import mock_mutuals

        rows = mock_mutuals(empty=mock_empty, target_name=target_name)
        network = rows_to_network(
            rows,
            target_name=target_name,
            target_url=target_url,
            seller_url=seller_url,
        )
        return {
            "network": {"contacts": network["contacts"]},
            "meta": {
                **network["meta"],
                "mock": True,
                "mutual_count": len(network["contacts"]),
                "source": "linkedin_session",
                "backend": cfg.backend,
            },
        }

    if not target_url:
        raise SessionMapError(
            "URL LinkedIn do alvo é obrigatória para mapear mutuals (sem inventar).",
            status=400,
        )

    profile_dir = (cfg.profile_dir or cfg.user_data_dir or "").strip()
    if not profile_dir:
        raise SessionMapError(
            "Sessão Camoufox não configurada. Rode bash scripts/setup_camoufox_profile.sh "
            "ou defina profile_dir em data/linkedin_session.yaml. "
            "Confira /api/linkedin-session/status. "
            "Ou use ?demo=1 / WARM_BRIDGE_SESSION_MOCK=1.",
            status=400,
        )

    handle: tuple[Any, ...] | None = None
    try:
        handle, rows = _fetch_mutuals(cfg, target_url)
        page = handle[2]
        network_pack = rows_to_network(
            rows,
            target_name=target_name,
            target_url=target_url,
            seller_url=seller_url,
        )
        contacts = network_pack["contacts"]
        target_snap: dict[str, str] = {
            "avatar_url": "",
            "photo": "",
            "title": "",
            "company": "",
            "headline": "",
        }
        seller_snap: dict[str, str] = dict(target_snap)

        if cfg.enrich:
            from .enrich import enrich_contacts, fetch_profile_snapshot

            if contacts:
                contacts = enrich_contacts(page, contacts, cap=cfg.enrich_cap)
            if target_url:
                target_snap = fetch_profile_snapshot(page, target_url)
            if seller_url:
                seller_snap = fetch_profile_snapshot(page, seller_url)

        return {
            "network": {"contacts": contacts},
            "meta": {
                **network_pack["meta"],
                "mock": False,
                "enriched": bool(cfg.enrich),
                "mutual_count": len(contacts),
                "source": "linkedin_session",
                "backend": cfg.backend,
                "target_avatar_url": target_snap.get("avatar_url") or "",
                "seller_avatar_url": seller_snap.get("avatar_url") or "",
                "target_title": target_snap.get("title") or "",
                "target_company": target_snap.get("company") or "",
                "target_headline": target_snap.get("headline") or "",
                "seller_title": seller_snap.get("title") or "",
                "seller_company": seller_snap.get("company") or "",
                "seller_headline": seller_snap.get("headline") or "",
                "enrich_cap": cfg.enrich_cap,
            },
        }
    except SessionMapError:
        raise
    except Exception as exc:  # noqa: BLE001
        from .session_status import friendly_map_error

        msg, status = friendly_map_error(exc)
        raise SessionMapError(msg, status=status) from exc
    finally:
        if handle is not None:
            _cleanup_handle(handle)
