"""Scrape mutual connections for a target profile — name + href only."""

from __future__ import annotations

import re
from typing import Any
from ..linkedin import normalize_linkedin_url
from .driver import RateLimit, polite_sleep


def _mutuals_url(profile_url: str) -> str:
    base = normalize_linkedin_url(profile_url) or profile_url.rstrip("/")
    return f"{base.rstrip('/')}/details/mutual-connections/"


def _parse_card(el: Any) -> dict[str, str] | None:
    """Best-effort parse of a LinkedIn search/list card."""
    try:
        link = el.find_element("css selector", "a[href*='/in/']")
    except Exception:  # noqa: BLE001
        return None
    href = (link.get_attribute("href") or "").split("?")[0]
    url = normalize_linkedin_url(href)
    if not url:
        return None
    name = (link.text or "").strip()
    if not name:
        try:
            name = (el.find_element("css selector", "span[aria-hidden='true']").text or "").strip()
        except Exception:  # noqa: BLE001
            name = ""
    if not name:
        # slug fallback — caller may enrich later
        m = re.search(r"/in/([^/]+)", url)
        name = (m.group(1).replace("-", " ").title() if m else "").strip()
    if not name:
        return None
    return {"name": name, "linkedin_url": url}


def fetch_mutuals(
    driver: Any,
    target_profile_url: str,
    *,
    rate: RateLimit | None = None,
    max_mutuals: int = 40,
) -> list[dict[str, str]]:
    """Navigate to target mutuals view and return observed name+url rows.

    Returns empty list when page has no mutuals or selectors miss — never invents.
    """
    rate = rate or RateLimit()
    url = _mutuals_url(target_profile_url)
    driver.get(url)
    polite_sleep(rate.between_nav_s)

    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    # LinkedIn DOM shifts often — try a few stable-ish selectors.
    selectors = [
        "div.entity-result__item",
        "li.reusable-search__result-container",
        "div[data-chameleon-result-urn]",
        "ul.reusable-search__entity-result-list > li",
        "div.scaffold-finite-scroll__content li",
    ]
    elements: list[Any] = []
    for sel in selectors:
        try:
            found = driver.find_elements("css selector", sel)
        except Exception:  # noqa: BLE001
            found = []
        if found:
            elements = found
            break

    if not elements:
        # Fallback: any profile anchors on the page
        try:
            anchors = driver.find_elements("css selector", "a[href*='/in/']")
        except Exception:  # noqa: BLE001
            anchors = []
        for a in anchors:
            href = (a.get_attribute("href") or "").split("?")[0]
            canon = normalize_linkedin_url(href)
            if not canon or canon in seen:
                continue
            # skip the target themselves
            target_canon = normalize_linkedin_url(target_profile_url)
            if target_canon and canon == target_canon:
                continue
            name = (a.text or "").strip()
            if not name or len(name) < 2:
                continue
            seen.add(canon)
            rows.append({"name": name, "linkedin_url": canon})
            if len(rows) >= max_mutuals:
                break
        polite_sleep(rate.after_action_s)
        return rows

    for el in elements:
        if len(rows) >= max_mutuals:
            break
        parsed = _parse_card(el)
        if not parsed:
            continue
        key = parsed["linkedin_url"]
        if key in seen:
            continue
        target_canon = normalize_linkedin_url(target_profile_url)
        if target_canon and key == target_canon:
            continue
        seen.add(key)
        rows.append(parsed)

    polite_sleep(rate.after_action_s)
    return rows
