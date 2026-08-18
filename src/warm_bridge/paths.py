from __future__ import annotations

import re
from typing import Any

from .models import ROOT, RankedBridge, Target, load_yaml


def _norm(s: str | None) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _tokens(s: str) -> set[str]:
    return {t for t in re.split(r"[^\w]+", _norm(s), flags=re.UNICODE) if len(t) > 2}


def _name_match(contact_name: str, target_name: str) -> bool:
    a, b = _norm(contact_name), _norm(target_name)
    if not a or not b:
        return False
    if a == b:
        return True
    # first+last containment for short names
    at, bt = _tokens(a), _tokens(b)
    return (len(at) >= 2 and at.issubset(bt)) or (len(bt) >= 2 and bt.issubset(at))


def _company_overlap(contact: dict[str, Any], company: str) -> tuple[bool, list[str]]:
    if not company:
        return False, []
    c = _norm(company)
    signals: list[str] = []
    if _norm(contact.get("company")) == c or c in _norm(contact.get("company")):
        signals.append("current_employer_match")
    for past in contact.get("past_companies") or []:
        if _norm(past) == c or c in _norm(past):
            signals.append("past_employer_match")
    if signals:
        signals.insert(0, "company_overlap")
        # dedupe preserve order
        seen: set[str] = set()
        out: list[str] = []
        for s in signals:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return True, out
    return False, []


def _notes_hints(contact: dict[str, Any], target: Target) -> list[str]:
    blob = _norm(" ".join([str(contact.get("notes") or ""), " ".join(contact.get("tags") or [])]))
    signals: list[str] = []
    tname = _norm(target.name)
    if tname and tname in blob:
        signals.append("notes_mention_target")
    company = _norm(target.company)
    if company and company in blob:
        signals.append("notes_mention_company")
    if "decision" in blob or "tomador" in blob:
        signals.append("tag_decision_maker")
    return signals


def _alumni(contact: dict[str, Any], target: Target, network: dict) -> list[str]:
    # Soft: shared school with any other contact marked as target-related is out of scope;
    # for v0, alumni fires when contact has schools AND title/company adjacency notes mention academia
    # Better: if target has school in a richer schema later. For now use school presence + company soft.
    signals: list[str] = []
    if contact.get("schools"):
        # alumni only as soft boost when also some company/title tie elsewhere — still list school_overlap
        # if notes mention school brands matching another contact is too heavy; keep simple signal
        if _norm(target.company) and (
            _norm(target.company) in _norm(contact.get("notes") or "")
            or any(_norm(target.company) in _norm(p) for p in (contact.get("past_companies") or []))
        ):
            signals.append("school_overlap")
        elif contact.get("schools") and not _company_overlap(contact, target.company)[0]:
            # weak alumni marker for people with school listed in same territory searches — skip bare
            pass
    for past in contact.get("past_companies") or []:
        if _norm(past) and _norm(past) == _norm(target.company):
            signals.append("past_company_overlap")
    return list(dict.fromkeys(signals))


def _title_adjacent(contact: dict[str, Any], target: Target, modes_doc: dict) -> list[str]:
    title = _norm(f"{contact.get('title') or ''} {target.title or ''}")
    adjacency = modes_doc.get("title_adjacency") or {}
    signals: list[str] = []
    target_title = _norm(target.title)
    contact_title = _norm(contact.get("title"))
    for _bucket, kws in adjacency.items():
        target_hit = any(k in target_title for k in kws)
        contact_hit = any(k in contact_title for k in kws)
        if target_hit and contact_hit:
            signals.append("title_keyword_overlap")
            signals.append("function_adjacent")
            break
    if not signals and target_title and contact_title:
        shared = _tokens(target_title) & _tokens(contact_title)
        if shared:
            signals.append("title_keyword_overlap")
    return list(dict.fromkeys(signals))


def _recency_key(days: int | None) -> str:
    if days is None:
        return "unknown"
    if days <= 30:
        return "within_30d"
    if days <= 90:
        return "within_90d"
    if days <= 365:
        return "within_365d"
    return "stale"


def _pick_mode(types: list[str], strength: str) -> str:
    if "direct" in types and strength in ("high", "medium", "unknown"):
        return "ask_intro" if strength == "high" else "ask_permission"
    if strength == "high" and any(t in types for t in ("same_company", "mutual_hint", "phone_warm")):
        return "ask_intro"
    if strength == "medium" and any(t in types for t in ("same_company", "mutual_hint", "phone_warm", "title_adjacent")):
        return "peer_forward"
    if strength == "low":
        return "ask_permission"
    if "alumni" in types or strength == "unknown":
        return "ask_intel" if "mutual_hint" in types or "same_company" in types else "ask_permission"
    if types:
        return "ask_intel"
    return "ask_permission"


def load_bridge_playbook() -> dict:
    return load_yaml(ROOT / "playbook" / "bridge-types.yaml")


def load_modes() -> dict:
    return load_yaml(ROOT / "playbook" / "modes.yaml")


def score_contact(
    contact: dict[str, Any],
    target: Target,
    playbook: dict | None = None,
    modes_doc: dict | None = None,
) -> RankedBridge | None:
    pb = playbook or load_bridge_playbook()
    modes_doc = modes_doc or load_modes()
    types_meta = pb["bridge_types"]
    strength = (contact.get("strength") or "unknown").lower()
    signals: list[str] = []
    matched_types: list[str] = []

    if _name_match(contact.get("name", ""), target.name):
        signals.extend(["name_match"])
        if "linkedin" in (contact.get("sources") or []):
            signals.append("linkedin_1st")
        if "phone" in (contact.get("sources") or []):
            signals.append("phone_match")
        matched_types.append("direct")

    ok, company_sigs = _company_overlap(contact, target.company)
    if ok:
        signals.extend(company_sigs)
        matched_types.append("same_company")

    note_sigs = _notes_hints(contact, target)
    if note_sigs:
        signals.extend(note_sigs)
        matched_types.append("mutual_hint")

    sources = set(contact.get("sources") or [])
    if "phone" in sources and strength == "high":
        # phone_warm if also some overlap OR notes hint
        if ok or note_sigs or _title_adjacent(contact, target, modes_doc):
            signals.extend(["source_phone", "high_trust"])
            if ok or note_sigs:
                signals.append("company_or_role_overlap")
            matched_types.append("phone_warm")

    alum = _alumni(contact, target, {})
    if alum:
        signals.extend(alum)
        matched_types.append("alumni")

    title_sigs = _title_adjacent(contact, target, modes_doc)
    if title_sigs and "direct" not in matched_types:
        signals.extend(title_sigs)
        matched_types.append("title_adjacent")

    # Deduplicate types preserving order
    matched_types = list(dict.fromkeys(matched_types))
    signals = list(dict.fromkeys(signals))

    if not matched_types:
        return None

    base = max(types_meta[t]["base_score"] for t in matched_types if t in types_meta)
    strength_m = pb.get("strength_multipliers", {}).get(strength, 0.85)
    rec_m = pb.get("recency_multipliers", {}).get(_recency_key(contact.get("last_touch_days")), 1.0)
    score = round(base * strength_m * rec_m, 4)

    min_score = pb.get("defaults", {}).get("min_score", 0.35)
    if score < min_score and "direct" not in matched_types:
        return None

    mode = _pick_mode(matched_types, strength)
    rationale = (
        f"types={matched_types} signals={signals} "
        f"strength={strength} recency={_recency_key(contact.get('last_touch_days'))}"
    )
    return RankedBridge(
        contact_id=str(contact.get("id") or contact.get("name")),
        name=contact.get("name") or "",
        score=score,
        types=matched_types,
        signals=signals,
        strength=strength,
        mode=mode,
        rationale=rationale,
        contact=contact,
    )


def find_bridges(network: dict, target: Target, top_k: int | None = None) -> list[RankedBridge]:
    pb = load_bridge_playbook()
    modes_doc = load_modes()
    k = top_k or pb.get("defaults", {}).get("top_k", 5)
    ranked: list[RankedBridge] = []
    for contact in network.get("contacts") or []:
        hit = score_contact(contact, target, pb, modes_doc)
        if hit:
            ranked.append(hit)
    ranked.sort(key=lambda r: (-r.score, r.name))
    return ranked[:k]
