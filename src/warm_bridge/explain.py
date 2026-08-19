"""Deterministic 'why this bridge' copy — the product proof, not a feature list.

Pulse-pattern from entrep: show *their* path data so the ask feels earned.
"""

from __future__ import annotations

from typing import Any

from .models import RankedBridge, Target
from .tutor import attach_tutor


def confidence_band(score: float, strength: str, types: list[str]) -> str:
    """Coarse bands — avoid fake precision like '87% fit'."""
    if "direct" in types:
        return "direct"
    if score >= 0.9 and strength == "high":
        return "high"
    if score >= 0.65:
        return "medium"
    return "low"


def path_label(bridge: RankedBridge, target: Target, locale: str = "pt") -> str:
    bridge_name = bridge.name.split()[0] if bridge.name else "?"
    target_name = target.name.split()[0] if target.name else "?"
    if "direct" in bridge.types:
        return f"Você → {target.name}" if locale == "pt" else f"You → {target.name}"
    if "same_company" in bridge.types:
        co = target.company or (bridge.contact.get("company") or "")
        if locale == "en":
            return f"{bridge.name} → {target.name} (same company: {co})"
        return f"{bridge.name} → {target.name} (mesma empresa: {co})"
    if "mutual_hint" in bridge.types:
        if locale == "en":
            return f"{bridge.name} → {target.name} (notes point to a tie)"
        return f"{bridge.name} → {target.name} (suas notas apontam ligação)"
    if "phone_warm" in bridge.types:
        if locale == "en":
            return f"{bridge_name} (phone-warm) → {target_name}"
        return f"{bridge_name} (celular / alta confiança) → {target_name}"
    if locale == "en":
        return f"{bridge.name} → {target.name}"
    return f"{bridge.name} → {target.name}"


def explain_bridge(bridge: RankedBridge, target: Target, locale: str = "pt") -> list[str]:
    why: list[str] = []
    types = set(bridge.types)
    c = bridge.contact

    if "direct" in types:
        why.append(
            "This person is already in your graph — message them directly."
            if locale == "en"
            else "Essa pessoa já está na sua rede — aborde direto."
        )
    if "same_company" in types:
        if "current_employer_match" in bridge.signals:
            why.append(
                f"Works at {target.company or c.get('company')} now."
                if locale == "en"
                else f"Trabalha hoje em {target.company or c.get('company')}."
            )
        if "past_employer_match" in bridge.signals:
            why.append(
                f"Previously at {target.company}."
                if locale == "en"
                else f"Já passou por {target.company}."
            )
    if "mutual_hint" in types:
        note = (c.get("notes") or "").strip()
        if note:
            snippet = note if len(note) <= 120 else note[:117] + "…"
            why.append(
                f"Your note: “{snippet}”" if locale == "en" else f"Sua anotação: “{snippet}”"
            )
        else:
            why.append(
                "Tags/notes mention the target or company."
                if locale == "en"
                else "Tags/notas mencionam o alvo ou a empresa."
            )
    if "phone_warm" in types:
        why.append(
            "Strong phone relationship — good for a WhatsApp ask."
            if locale == "en"
            else "Relação forte no celular — bom pedido por WhatsApp."
        )
    if "title_adjacent" in types:
        why.append(
            f"Title adjacent to buyer role ({c.get('title') or '—'} ↔ {target.title or '—'})."
            if locale == "en"
            else f"Cargo próximo do comprador ({c.get('title') or '—'} ↔ {target.title or '—'})."
        )
    if "alumni" in types:
        schools = ", ".join(c.get("schools") or []) or "shared background"
        why.append(
            f"Soft tie ({schools}). Prefer permission/intel over hard intro."
            if locale == "en"
            else f"Laço fraco ({schools}). Prefira permissão/intel a intro dura."
        )

    strength = bridge.strength
    if strength == "high":
        why.append("You marked this relationship as high trust." if locale == "en" else "Você marcou esta relação como alta confiança.")
    elif strength == "low":
        why.append("Low trust — soft ask only." if locale == "en" else "Baixa confiança — pedido leve apenas.")

    days = c.get("last_touch_days")
    if isinstance(days, int):
        if days <= 30:
            why.append("Recent touch (<30d)." if locale == "en" else "Contato recente (<30d).")
        elif days > 365:
            why.append("Stale relationship (>1y) — re-warm before asking." if locale == "en" else "Relação fria (>1 ano) — reaqueça antes de pedir.")

    return why[:5]


def enrich_ranked(
    ranked: list[RankedBridge],
    target: Target,
    locale: str = "pt",
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for b in ranked:
        mode = "direct" if "direct" in b.types else b.mode
        band = confidence_band(b.score, b.strength, b.types)
        out.append(
            {
                "contact_id": b.contact_id,
                "name": b.name,
                "score": b.score,
                "types": b.types,
                "signals": b.signals,
                "strength": b.strength,
                "mode": mode,
                "confidence": band,
                "bucket": "direct" if "direct" in b.types else "bridge",
                "path_label": path_label(b, target, locale),
                "why": explain_bridge(b, target, locale),
                "rationale": b.rationale,
                "title": b.contact.get("title") or "",
                "company": b.contact.get("company") or "",
                "phone": b.contact.get("phone") or "",
                "linkedin_url": b.contact.get("linkedin_url") or "",
                "sources": b.contact.get("sources") or [],
            }
        )
    for row in out:
        attach_tutor(row, locale=locale)
    return out
