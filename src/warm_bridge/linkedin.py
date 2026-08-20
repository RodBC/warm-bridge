"""LinkedIn URL helpers — identity only. No scraping, no session hijack."""

from __future__ import annotations

import re
from urllib.parse import unquote, urlparse

# linkedin.com/in/slug or /pub/...
_IN_PATH = re.compile(
    r"^/(?:in|pub)/([^/?#]+)/?",
    re.IGNORECASE,
)
_BARE = re.compile(
    r"(?:https?://)?(?:www\.)?linkedin\.com/(?:in|pub)/([^/?#\s]+)",
    re.IGNORECASE,
)


def linkedin_slug(value: str | None) -> str | None:
    """Extract profile slug from a LinkedIn URL or bare path. None if not LinkedIn."""
    raw = (value or "").strip()
    if not raw:
        return None
    if "linkedin.com" in raw.lower():
        m = _BARE.search(raw)
        if m:
            return unquote(m.group(1)).strip("/").lower() or None
        try:
            path = urlparse(raw if "://" in raw else f"https://{raw}").path or ""
        except Exception:  # noqa: BLE001
            return None
        m2 = _IN_PATH.match(path)
        return unquote(m2.group(1)).strip("/").lower() if m2 else None
    # bare slug typed as "marina-costa"
    if re.fullmatch(r"[a-zA-Z0-9\-_%]{2,100}", raw) and "-" in raw:
        return unquote(raw).lower()
    return None


def normalize_linkedin_url(value: str | None) -> str | None:
    """Canonical https://www.linkedin.com/in/{slug} or None."""
    slug = linkedin_slug(value)
    if not slug:
        # already a full-ish URL without /in/? keep if looks like linkedin
        raw = (value or "").strip()
        if raw and "linkedin.com" in raw.lower():
            if not raw.startswith("http"):
                return f"https://{raw.lstrip('/')}"
            return raw
        return None
    return f"https://www.linkedin.com/in/{slug}"


def display_name_from_linkedin(value: str | None) -> str | None:
    """Best-effort name from slug: marina-costa → Marina Costa. Not identity proof."""
    slug = linkedin_slug(value)
    if not slug:
        return None
    parts = [p for p in re.split(r"[-_]+", slug) if p and not p.isdigit()]
    if not parts:
        return None
    return " ".join(p[:1].upper() + p[1:] for p in parts)


def resolve_target_fields(
    name: str = "",
    company: str = "",
    title: str = "",
    linkedin: str = "",
) -> dict[str, str]:
    """Fill name from LinkedIn slug when user only pasted a profile URL."""
    url = normalize_linkedin_url(linkedin) or normalize_linkedin_url(name) or ""
    out_name = (name or "").strip()
    if url and (not out_name or linkedin_slug(out_name)):
        # name field was itself a URL, or empty
        guessed = display_name_from_linkedin(url)
        if guessed:
            out_name = guessed
    if not out_name and url:
        out_name = display_name_from_linkedin(url) or "Alvo LinkedIn"
    return {
        "name": out_name,
        "company": (company or "").strip(),
        "title": (title or "").strip(),
        "linkedin_url": url,
    }
