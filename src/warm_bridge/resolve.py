"""Target identity resolution against the seller's graph.

Inspired by entrep/ReclameAqui identity resolution — audit trail, not magic:
CONFIRMED | LIKELY | NOT_IN_GRAPH. Never invent people outside the import.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from typing import Any

from .models import Target
from .paths import _company_overlap, _name_match, _norm, _tokens


@dataclass
class Resolution:
    status: str  # CONFIRMED | LIKELY | NOT_IN_GRAPH
    contact_id: str | None
    contact_name: str | None
    score: float
    rationale: str
    candidates: list[dict[str, Any]]


def _name_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    if _name_match(a, b):
        return 1.0
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def resolve_target(network: dict[str, Any], target: Target) -> Resolution:
    """Find whether the decision-maker already sits in the imported graph."""
    candidates: list[tuple[float, dict[str, Any], str]] = []
    for contact in network.get("contacts") or []:
        name_score = _name_similarity(contact.get("name") or "", target.name)
        if name_score < 0.55:
            continue
        company_ok, _ = _company_overlap(contact, target.company)
        title_overlap = 0.0
        if target.title and contact.get("title"):
            shared = _tokens(target.title) & _tokens(str(contact.get("title")))
            if shared:
                title_overlap = 0.15
        score = name_score
        if company_ok:
            score += 0.25
        score += title_overlap
        why = []
        if name_score >= 0.99:
            why.append("exact/near name match")
        elif name_score >= 0.8:
            why.append(f"fuzzy name ({name_score:.2f})")
        else:
            why.append(f"weak name ({name_score:.2f})")
        if company_ok:
            why.append("company overlap")
        if title_overlap:
            why.append("title overlap")
        candidates.append((min(score, 1.0), contact, "; ".join(why)))

    candidates.sort(key=lambda x: -x[0])
    top = candidates[:5]
    payload = [
        {
            "contact_id": c.get("id"),
            "name": c.get("name"),
            "company": c.get("company"),
            "title": c.get("title"),
            "score": round(s, 3),
            "why": w,
        }
        for s, c, w in top
    ]

    if not top:
        return Resolution(
            status="NOT_IN_GRAPH",
            contact_id=None,
            contact_name=None,
            score=0.0,
            rationale="No contact name resembled the target in the imported network.",
            candidates=[],
        )

    best_score, best, why = top[0]
    company_ok, _ = _company_overlap(best, target.company)
    if best_score >= 0.95 and (_name_match(best.get("name") or "", target.name) or company_ok):
        status = "CONFIRMED"
    elif best_score >= 0.75:
        status = "LIKELY"
    else:
        status = "NOT_IN_GRAPH"

    matched = status in ("CONFIRMED", "LIKELY")
    return Resolution(
        status=status,
        contact_id=str(best.get("id")) if matched else None,
        contact_name=str(best.get("name")) if matched else None,
        score=round(best_score, 3),
        rationale=why if matched else "Closest names were too weak to claim a match.",
        candidates=payload,
    )


def resolution_as_dict(res: Resolution) -> dict[str, Any]:
    return asdict(res)
