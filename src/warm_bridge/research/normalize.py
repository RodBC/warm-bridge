"""Normalize search hits into insight items with kind labels."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

JUNK_DOMAINS = frozenset(
    {
        "facebook.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "tiktok.com",
        "youtube.com",
    }
)


def _domain(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:  # noqa: BLE001
        return ""


def classify_kind(url: str, title: str, snippet: str, company: str) -> str:
    low_url = url.lower()
    text = f"{title} {snippet}".lower()
    company_low = (company or "").lower()
    if "linkedin.com" in low_url:
        return "profile_hint"
    if any(x in low_url for x in ("news", "reuters", "bloomberg", "globo", "valor")):
        return "news"
    if company_low and company_low in text:
        return "company"
    if re.search(r"\b(ceo|diretor|head|vp|founder|presidente)\b", text):
        return "profile_hint"
    return "other"


def normalize_items(
    raw_rows: list[dict[str, str]],
    *,
    company: str,
    max_items: int = 8,
) -> list[dict[str, Any]]:
    seen_urls: set[str] = set()
    out: list[dict[str, Any]] = []
    for row in raw_rows:
        url = (row.get("url") or "").strip()
        title = (row.get("title") or "").strip()
        snippet = (row.get("snippet") or "").strip()
        if not url or not title:
            continue
        dom = _domain(url)
        if dom in JUNK_DOMAINS:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)
        out.append(
            {
                "title": title,
                "url": url,
                "snippet": snippet,
                "kind": classify_kind(url, title, snippet, company),
                "domain": dom,
            }
        )
        if len(out) >= max_items:
            break
    return out
