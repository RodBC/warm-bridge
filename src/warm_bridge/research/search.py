"""Fetch public search results via DuckDuckGo HTML (no API key)."""

from __future__ import annotations

import re
import time
import urllib.parse
import urllib.request
from html import unescape
from typing import Any

_USER_AGENT = (
    "WarmBridge/0.2 (+local research; public pages only; "
    "https://github.com/RodBC/warm-bridge)"
)
_LAST_QUERY_AT = 0.0
_MIN_INTERVAL_S = 1.2


def _polite_wait() -> None:
    global _LAST_QUERY_AT
    elapsed = time.monotonic() - _LAST_QUERY_AT
    if elapsed < _MIN_INTERVAL_S:
        time.sleep(_MIN_INTERVAL_S - elapsed)
    _LAST_QUERY_AT = time.monotonic()


def build_queries(
    name: str,
    company: str,
    title: str = "",
    linkedin_url: str = "",
) -> list[str]:
    """Deterministic query set for target research."""
    queries: list[str] = []
    name = (name or "").strip()
    company = (company or "").strip()
    title = (title or "").strip()
    if name and company:
        queries.append(f'"{name}" "{company}"')
        if title:
            queries.append(f'"{name}" {title} {company}')
        queries.append(f'{company} news')
    elif name:
        queries.append(name)
        if title:
            queries.append(f"{name} {title}")
    elif company:
        queries.append(f"{company} news")
        queries.append(f"{company} leadership")
    if linkedin_url and "linkedin.com/in/" in linkedin_url:
        slug = linkedin_url.split("/in/")[-1].split("?")[0].strip("/")
        if slug and name:
            queries.append(f'"{name}" linkedin')
    return queries[:4]


def _fetch_html(query: str, timeout: float = 12.0) -> str:
    _polite_wait()
    url = "https://html.duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _parse_ddg_html(html: str) -> list[dict[str, str]]:
    """Parse DuckDuckGo HTML lite result blocks."""
    results: list[dict[str, str]] = []
    # Result links: class result__a
    pattern = re.compile(
        r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL | re.IGNORECASE,
    )
    for match in pattern.finditer(html):
        href = unescape(match.group(1))
        title = re.sub(r"<[^>]+>", "", unescape(match.group(2))).strip()
        snippet = re.sub(r"<[^>]+>", "", unescape(match.group(3))).strip()
        if not href or not title:
            continue
        # DDG redirect wrapper
        if "uddg=" in href:
            parsed = urllib.parse.urlparse(href)
            qs = urllib.parse.parse_qs(parsed.query)
            if "uddg" in qs:
                href = qs["uddg"][0]
        results.append({"title": title[:200], "url": href[:500], "snippet": snippet[:400]})
    if not results:
        # Fallback: simpler link pattern
        for m in re.finditer(
            r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>',
            html,
            re.I,
        ):
            href = unescape(m.group(1))
            title = unescape(m.group(2)).strip()
            if title and href:
                if "uddg=" in href:
                    parsed = urllib.parse.urlparse(href)
                    qs = urllib.parse.parse_qs(parsed.query)
                    if "uddg" in qs:
                        href = qs["uddg"][0]
                results.append({"title": title[:200], "url": href[:500], "snippet": ""})
    return results


def search_public(query: str, max_results: int = 5) -> list[dict[str, str]]:
    """Run one public search query; return raw title/url/snippet rows."""
    try:
        html = _fetch_html(query)
        return _parse_ddg_html(html)[:max_results]
    except Exception:  # noqa: BLE001
        return []
