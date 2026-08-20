"""map_target: seller session + target → observed network dict."""

from __future__ import annotations

import os
from typing import Any

from ..linkedin import normalize_linkedin_url, resolve_target_fields
from .config import SessionConfig, load_session_config
from .normalize import rows_to_network


class SeleniumMapError(Exception):
    """Driver/session failure — surface as 400/503, never invent contacts."""

    def __init__(self, message: str, *, status: int = 503) -> None:
        super().__init__(message)
        self.status = status


def _use_mock() -> bool:
    return os.environ.get("WARM_BRIDGE_SELENIUM_MOCK", "").strip() in ("1", "true", "yes")


def map_target(
    seller_linkedin: str,
    target_fields: dict[str, str],
    session_cfg: SessionConfig | None = None,
    *,
    mock: bool | None = None,
    mock_empty: bool = False,
) -> dict[str, Any]:
    """Return `{network, meta}` from session-observed mutuals (or mock fixture).

    Never fabricates mutuals. Empty scrape → empty contacts.
    """
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
                "source": "linkedin_selenium",
            },
        }

    if not target_url:
        raise SeleniumMapError(
            "URL LinkedIn do alvo é obrigatória para mapear mutuals (sem inventar).",
            status=400,
        )
    if not cfg.user_data_dir:
        raise SeleniumMapError(
            "Sessão Chrome não configurada. Rode bash scripts/setup_chrome_profile.sh "
            "ou defina user_data_dir em data/linkedin_session.yaml / "
            "WARM_BRIDGE_CHROME_USER_DATA. Confira o painel Sessão LinkedIn "
            "(/api/linkedin-session/status). Ou use ?demo=1 / WARM_BRIDGE_SELENIUM_MOCK=1.",
            status=400,
        )

    from .driver import RateLimit, build_chrome, quit_driver
    from .mutuals import fetch_mutuals

    driver = None
    try:
        driver = build_chrome(cfg)
        rows = fetch_mutuals(
            driver,
            target_url,
            rate=RateLimit(),
            max_mutuals=cfg.max_mutuals,
        )
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
        seller_snap: dict[str, str] = {
            "avatar_url": "",
            "photo": "",
            "title": "",
            "company": "",
            "headline": "",
        }

        if cfg.enrich:
            from .enrich import enrich_contacts, fetch_profile_snapshot

            if contacts:
                contacts = enrich_contacts(
                    driver,
                    contacts,
                    cap=cfg.enrich_cap,
                )
            if target_url:
                target_snap = fetch_profile_snapshot(driver, target_url)
            if seller_url:
                seller_snap = fetch_profile_snapshot(driver, seller_url)

        return {
            "network": {"contacts": contacts},
            "meta": {
                **network_pack["meta"],
                "mock": False,
                "enriched": bool(cfg.enrich),
                "mutual_count": len(contacts),
                "source": "linkedin_selenium",
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
    except SeleniumMapError:
        raise
    except Exception as exc:  # noqa: BLE001
        from .session_status import friendly_map_error

        msg, status = friendly_map_error(exc)
        raise SeleniumMapError(msg, status=status) from exc
    finally:
        if driver is not None:
            quit_driver(driver)
