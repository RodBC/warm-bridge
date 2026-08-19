"""Account workspace — several decision-makers under one company.

Pro-tier wedge: map an account once, see path proof per buyer, drill into asks.
Reuses the same find pipeline — no parallel scoring logic.
"""

from __future__ import annotations

from typing import Any

from .approach import approaches_for_ranked
from .explain import enrich_ranked
from .models import RankedBridge, Target
from .paths import find_bridges
from .resolve import resolution_as_dict, resolve_target


def proof_line(
    bridges: list[dict[str, Any]],
    directs: list[dict[str, Any]],
    target: Target,
    locale: str,
) -> str:
    if bridges:
        top = bridges[0]
        if locale == "en":
            return f"Best path: {top['path_label']} · confidence {top['confidence']} · mode {top['mode']}"
        return f"Melhor caminho: {top['path_label']} · confiança {top['confidence']} · modo {top['mode']}"
    if directs:
        if locale == "en":
            return f"You already have {target.name} in your graph — message them directly."
        return f"Você já tem {target.name} na rede — aborde direto."
    if locale == "en":
        return "No warm path found yet — add notes, phone contacts, or company tags and retry."
    return "Nenhuma ponte quente ainda — acrescente notas, contatos do celular ou tags de empresa e tente de novo."


def build_find_result(
    *,
    network: dict[str, Any],
    seller: dict[str, Any],
    target: Target,
    locale: str = "pt",
    top_k: int = 8,
    with_approaches: bool = True,
) -> dict[str, Any]:
    """Single-target find — shared by /api/find and account workspace."""
    resolution = resolve_target(network, target)
    ranked = find_bridges(network, target, top_k=top_k)
    enriched = enrich_ranked(ranked, target, locale=locale)

    bridges = [e for e in enriched if e["bucket"] == "bridge"]
    directs = [e for e in enriched if e["bucket"] == "direct"]

    if with_approaches and ranked:
        approaches = approaches_for_ranked(seller, target, ranked, locale=locale)
        by_id = {a["contact_id"]: a for a in approaches}
        for e in enriched:
            draft = by_id.get(e["contact_id"])
            if draft:
                e["message"] = draft["message"]

    return {
        "target": target.__dict__,
        "locale": locale,
        "resolution": resolution_as_dict(resolution),
        "counts": {
            "network": len(network.get("contacts") or []),
            "bridges": len(bridges),
            "direct": len(directs),
        },
        "bridges": bridges,
        "direct": directs,
        "proof_line": proof_line(bridges, directs, target, locale),
        "note": (
            "Você envia a mensagem. O produto é achar a ponte + o pedido certo — "
            "não disparar spam pela sua rede."
            if locale != "en"
            else "You send the message. We find the bridge and the right ask — not spam through your network."
        ),
    }


def _target_row(
    *,
    target_id: str,
    name: str,
    title: str,
    company: str,
    find_result: dict[str, Any],
) -> dict[str, Any]:
    bridges = find_result["bridges"]
    directs = find_result["direct"]
    top = bridges[0] if bridges else (directs[0] if directs else None)
    has_path = bool(bridges or directs)
    return {
        "id": target_id,
        "name": name,
        "title": title,
        "company": company,
        "has_path": has_path,
        "proof_line": find_result["proof_line"],
        "top_bridge_name": top["name"] if top else None,
        "top_confidence": top["confidence"] if top else None,
        "bridge_count": find_result["counts"]["bridges"],
        "direct_count": find_result["counts"]["direct"],
        "find": find_result,
    }


def find_account(
    *,
    network: dict[str, Any],
    seller: dict[str, Any],
    company: str,
    targets: list[dict[str, Any]],
    locale: str = "pt",
    top_k: int = 8,
    with_approaches: bool = True,
) -> dict[str, Any]:
    """Map warm paths for every buyer at an account."""
    company = (company or "").strip()
    rows: list[dict[str, Any]] = []

    for i, raw in enumerate(targets):
        name = (raw.get("name") or "").strip()
        if not name:
            continue
        tid = (raw.get("id") or f"t_{i}").strip()
        title = (raw.get("title") or "").strip()
        target = Target(name=name, company=company, title=title)
        find_result = build_find_result(
            network=network,
            seller=seller,
            target=target,
            locale=locale,
            top_k=top_k,
            with_approaches=with_approaches,
        )
        rows.append(
            _target_row(
                target_id=tid,
                name=name,
                title=title,
                company=company,
                find_result=find_result,
            )
        )

    with_path = sum(1 for r in rows if r["has_path"])
    total = len(rows)
    if locale == "en":
        summary = f"{with_path} of {total} targets have a warm path at {company or 'this account'}"
    else:
        summary = f"{with_path} de {total} alvos com caminho quente em {company or 'esta conta'}"

    return {
        "company": company,
        "locale": locale,
        "summary_line": summary,
        "with_path": with_path,
        "total_targets": total,
        "targets": rows,
    }
