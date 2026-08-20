"""Map scrape rows → Warm Bridge contact dicts."""

from __future__ import annotations

from typing import Any

from ..imports import contact_from_fields


def mutual_row_to_contact(
    row: dict[str, Any],
    *,
    target_name: str,
    strength: str = "medium",
) -> dict[str, Any]:
    name = (row.get("name") or "").strip()
    url = (row.get("linkedin_url") or "").strip()
    company = (row.get("company") or "").strip()
    title = (row.get("title") or "").strip()
    avatar = (row.get("avatar_url") or row.get("photo") or "").strip()
    notes = f"LinkedIn mutual with {target_name}." if target_name else "LinkedIn mutual (session)."
    extra_notes = (row.get("notes") or "").strip()
    if extra_notes:
        notes = f"{notes} {extra_notes}".strip()
    return contact_from_fields(
        name=name,
        company=company,
        title=title,
        notes=notes,
        sources=["linkedin_session"],
        strength=strength,
        linkedin_url=url,
        contact_id=row.get("id"),
        avatar_url=avatar,
    )


def rows_to_network(
    rows: list[dict[str, Any]],
    *,
    target_name: str,
    target_url: str = "",
    seller_url: str = "",
) -> dict[str, Any]:
    contacts = [mutual_row_to_contact(r, target_name=target_name) for r in rows if (r.get("name") or "").strip()]
    return {
        "contacts": contacts,
        "meta": {
            "source": "linkedin_session",
            "target_name": target_name,
            "target_url": target_url,
            "seller_url": seller_url,
            "mutual_count": len(contacts),
        },
    }
