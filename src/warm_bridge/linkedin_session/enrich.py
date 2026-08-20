"""Optional profile enrich — title, company, avatar_url for top mutuals."""

from __future__ import annotations

from typing import Any

from ..linkedin import normalize_linkedin_url
from .driver.rate_limit import RateLimit, polite_sleep

_AVATAR_SELECTORS = [
    "img.pv-top-card-profile-picture__image--show",
    "img.pv-top-card-profile-picture__image",
    "button.pv-top-card-profile-picture img",
    "div.profile-photo-edit__preview img",
    "img[src*='profile-displayphoto']",
    "img[src*='media.licdn.com'][class*='profile']",
    "section.artdeco-card img[src*='media.licdn.com']",
]

_HEADLINE_SELECTORS = [
    "div.text-body-medium",
    "div.ph5.pb5 div.text-body-medium",
    ".pv-text-details__left-panel .text-body-medium",
]


def extract_avatar_url(page: Any) -> str:
    for sel in _AVATAR_SELECTORS:
        try:
            imgs = page.find_elements("css selector", sel)
        except Exception:  # noqa: BLE001
            continue
        for img in imgs:
            src = (img.get_attribute("src") or img.get_attribute("data-delayed-url") or "").strip()
            if not src.startswith("http"):
                continue
            if "data:image" in src:
                continue
            if "static.licdn" in src and "ghost" in src.lower():
                continue
            return src
    return ""


def _split_headline(text: str) -> tuple[str, str]:
    raw = (text or "").strip()
    if not raw or len(raw) > 220:
        return "", ""
    for sep in (" at ", " @ ", " - ", " – ", " — ", " | "):
        if sep in raw:
            left, right = raw.split(sep, 1)
            title, company = left.strip(), right.strip()
            if title and company and len(company) < 120:
                return title, company
    return raw, ""


def extract_headline(page: Any) -> str:
    for sel in _HEADLINE_SELECTORS:
        try:
            el = page.find_element("css selector", sel)
            text = (el.text or "").strip()
            if text and len(text) < 220:
                return text
        except Exception:  # noqa: BLE001
            continue
    return ""


def extract_company(page: Any) -> str:
    selectors = [
        "button[aria-label*='Current company'] span",
        "button[aria-label*='Company'] span",
        "div[data-field='experience'] span",
        "ul.pv-top-card--experience-list li span",
    ]
    for sel in selectors:
        try:
            el = page.find_element("css selector", sel)
            text = (el.text or "").strip()
            if text and len(text) < 120:
                return text
        except Exception:  # noqa: BLE001
            continue
    return ""


def enrich_profile_fields(page: Any, row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    headline = extract_headline(page)
    if headline:
        title, company_from_headline = _split_headline(headline)
        if not out.get("title") and title:
            out["title"] = title
        if not out.get("company") and company_from_headline:
            out["company"] = company_from_headline
        if not out.get("headline"):
            out["headline"] = headline

    if not out.get("company"):
        company = extract_company(page)
        if company:
            out["company"] = company

    if not out.get("avatar_url") and not out.get("photo"):
        src = extract_avatar_url(page)
        if src:
            out["avatar_url"] = src
            out["photo"] = src
    elif out.get("avatar_url") and not out.get("photo"):
        out["photo"] = out["avatar_url"]
    elif out.get("photo") and not out.get("avatar_url"):
        out["avatar_url"] = out["photo"]
    return out


def fetch_profile_snapshot(
    page: Any,
    profile_url: str,
    *,
    rate: RateLimit | None = None,
) -> dict[str, str]:
    url = normalize_linkedin_url(profile_url)
    empty = {"avatar_url": "", "photo": "", "title": "", "company": "", "headline": ""}
    if not url:
        return empty
    rate = rate or RateLimit(between_nav_s=1.8, after_action_s=0.4)
    try:
        page.get(url)
        polite_sleep(rate.between_nav_s)
        row = enrich_profile_fields(page, {})
        polite_sleep(rate.after_action_s)
        return {
            "avatar_url": str(row.get("avatar_url") or row.get("photo") or ""),
            "photo": str(row.get("photo") or row.get("avatar_url") or ""),
            "title": str(row.get("title") or ""),
            "company": str(row.get("company") or ""),
            "headline": str(row.get("headline") or ""),
        }
    except Exception:  # noqa: BLE001
        return empty


def enrich_contacts(
    page: Any,
    contacts: list[dict[str, Any]],
    *,
    cap: int = 16,
    rate: RateLimit | None = None,
) -> list[dict[str, Any]]:
    rate = rate or RateLimit(between_nav_s=2.0, after_action_s=0.6)
    out: list[dict[str, Any]] = []
    for i, c in enumerate(contacts):
        row = dict(c)
        if i >= cap:
            out.append(row)
            continue
        url = normalize_linkedin_url(row.get("linkedin_url") or "")
        if not url:
            out.append(row)
            continue
        try:
            page.get(url)
            polite_sleep(rate.between_nav_s)
            row = enrich_profile_fields(page, row)
            polite_sleep(rate.after_action_s)
        except Exception:  # noqa: BLE001
            pass
        out.append(row)
    return out
