"""User-owned network intake — LinkedIn export, phone CSV, paste cards.

No scraping. Same posture as Career Fit recruiter paste: you bring the data.
"""

from __future__ import annotations

import csv
import io
import re
import uuid
from typing import Any


EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
URL_RE = re.compile(r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?", re.I)


def _gid(prefix: str = "c") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _first_name(name: str) -> str:
    parts = (name or "").strip().split()
    return parts[0] if parts else ""


def _get_row(row: dict[str, str | None], *keys: str) -> str:
    normalized = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
    for key in keys:
        if key in normalized and normalized[key]:
            return normalized[key]
    return ""


def contact_from_fields(
    *,
    name: str,
    company: str = "",
    title: str = "",
    notes: str = "",
    sources: list[str] | None = None,
    strength: str = "unknown",
    linkedin_url: str = "",
    email: str = "",
    phone: str = "",
    past_companies: list[str] | None = None,
    schools: list[str] | None = None,
    tags: list[str] | None = None,
    last_touch_days: int | None = None,
    contact_id: str | None = None,
    avatar_url: str = "",
    photo: str = "",
) -> dict[str, Any]:
    pic = (avatar_url or photo or "").strip()
    out: dict[str, Any] = {
        "id": contact_id or _gid(),
        "name": name.strip() or "Unknown",
        "first_name": _first_name(name),
        "sources": sources or ["paste"],
        "company": company.strip(),
        "title": title.strip(),
        "strength": (strength or "unknown").lower(),
        "last_touch_days": last_touch_days,
        "schools": schools or [],
        "past_companies": past_companies or [],
        "notes": notes.strip(),
        "tags": tags or [],
        "linkedin_url": linkedin_url.strip(),
        "email": email.strip(),
        "phone": phone.strip(),
    }
    if pic:
        out["avatar_url"] = pic
        out["photo"] = pic
    return out


def parse_linkedin_connections_csv(content: str) -> list[dict[str, Any]]:
    """Parse LinkedIn 'Connections.csv' export (Notes skipped until header row)."""
    text = content.lstrip("\ufeff")
    # LinkedIn often puts a Notes disclaimer before the header
    lines = text.splitlines()
    header_idx = 0
    for i, line in enumerate(lines):
        low = line.lower()
        if "first name" in low and "last name" in low:
            header_idx = i
            break
    body = "\n".join(lines[header_idx:])
    reader = csv.DictReader(io.StringIO(body))
    contacts: list[dict[str, Any]] = []
    for row in reader:
        first = _get_row(row, "first name", "firstname")
        last = _get_row(row, "last name", "lastname")
        name = f"{first} {last}".strip() or _get_row(row, "name", "full name")
        if not name:
            continue
        url = _get_row(row, "url", "profile url", "linkedin", "linkedin url")
        email = _get_row(row, "email address", "email", "e-mail")
        company = _get_row(row, "company", "empresa", "organization")
        title = _get_row(row, "position", "title", "cargo", "headline")
        connected = _get_row(row, "connected on", "connected")
        notes = f"LinkedIn connection since {connected}." if connected else ""
        contacts.append(
            contact_from_fields(
                name=name,
                company=company,
                title=title,
                notes=notes,
                sources=["linkedin"],
                linkedin_url=url,
                email=email,
                strength="medium",
            )
        )
    return contacts


def parse_phone_csv(content: str) -> list[dict[str, Any]]:
    """Flexible phone-book CSV: name, phone, company, title, notes, strength."""
    text = content.lstrip("\ufeff")
    reader = csv.DictReader(io.StringIO(text))
    contacts: list[dict[str, Any]] = []
    for row in reader:
        name = _get_row(row, "name", "nome", "full name")
        if not name:
            continue
        phone = _get_row(row, "phone", "telefone", "mobile", "celular") or (
            PHONE_RE.search(" ".join(str(v) for v in row.values() if v)).group(0)
            if PHONE_RE.search(" ".join(str(v) for v in row.values() if v))
            else ""
        )
        contacts.append(
            contact_from_fields(
                name=name,
                company=_get_row(row, "company", "empresa"),
                title=_get_row(row, "title", "cargo", "position"),
                notes=_get_row(row, "notes", "notas", "obs"),
                sources=["phone"],
                strength=_get_row(row, "strength", "força", "confianca", "confiança") or "high",
                phone=phone,
                email=_get_row(row, "email", "e-mail"),
            )
        )
    return contacts


def parse_paste_block(block: str) -> dict[str, Any]:
    lines = [ln.strip() for ln in block.strip().splitlines() if ln.strip()]
    name = lines[0] if lines else "Unknown"
    title = ""
    company = ""
    notes_parts: list[str] = []
    linkedin_url = ""
    for ln in lines[1:]:
        low = ln.lower()
        m = URL_RE.search(ln)
        if m:
            linkedin_url = m.group(0)
            if not linkedin_url.startswith("http"):
                linkedin_url = "https://" + linkedin_url
            continue
        if ("|" in ln or "·" in ln or " @ " in ln) and not title:
            cleaned = ln.replace("·", "|")
            parts = [p.strip() for p in cleaned.split("|") if p.strip()]
            title = parts[0] if parts else ln
            if len(parts) > 1:
                company = parts[-1]
            continue
        if low.startswith("empresa:") or low.startswith("company:"):
            company = ln.split(":", 1)[1].strip()
            continue
        notes_parts.append(ln)
    blob = "\n".join(lines)
    return contact_from_fields(
        name=name,
        company=company,
        title=title,
        notes="\n".join(notes_parts),
        sources=["paste"],
        linkedin_url=linkedin_url,
        email=(EMAIL_RE.search(blob).group(0) if EMAIL_RE.search(blob) else ""),
        phone=(PHONE_RE.search(blob).group(0).strip() if PHONE_RE.search(blob) else ""),
        strength="medium",
    )


def parse_contacts_paste(text: str) -> list[dict[str, Any]]:
    chunks = re.split(r"\n\s*\n", text.strip())
    return [parse_paste_block(c) for c in chunks if c.strip()]


def detect_and_parse(text: str) -> tuple[str, list[dict[str, Any]]]:
    """Auto-detect LinkedIn export vs phone CSV vs paste cards."""
    raw = text.lstrip("\ufeff").strip()
    if not raw:
        return "empty", []
    head = "\n".join(raw.splitlines()[:8]).lower()
    if "first name" in head and ("last name" in head or "company" in head):
        return "linkedin_csv", parse_linkedin_connections_csv(raw)
    if head.startswith("name,") or "\nname," in head[:120]:
        # phone-ish if phone column present
        if "phone" in head or "telefone" in head or "celular" in head:
            return "phone_csv", parse_phone_csv(raw)
        return "generic_csv", parse_phone_csv(raw)
    return "paste", parse_contacts_paste(raw)


def merge_networks(*networks: dict[str, Any]) -> dict[str, Any]:
    """Merge contact lists; later ids win on same normalized name+company."""
    by_key: dict[str, dict[str, Any]] = {}
    for net in networks:
        for c in net.get("contacts") or []:
            key = f"{(c.get('name') or '').strip().lower()}|{(c.get('company') or '').strip().lower()}"
            if key in by_key:
                prev = by_key[key]
                # merge sources and notes
                sources = list(dict.fromkeys((prev.get("sources") or []) + (c.get("sources") or [])))
                notes = " | ".join(x for x in [prev.get("notes") or "", c.get("notes") or ""] if x)
                merged = {**prev, **{k: v for k, v in c.items() if v not in (None, "", [])}}
                merged["sources"] = sources
                merged["notes"] = notes
                if prev.get("strength") == "high" or c.get("strength") == "high":
                    merged["strength"] = "high"
                by_key[key] = merged
            else:
                by_key[key] = dict(c)
    return {"contacts": list(by_key.values())}


def network_from_text(text: str) -> dict[str, Any]:
    kind, contacts = detect_and_parse(text)
    return {"contacts": contacts, "import_kind": kind}
