"""research_target — public insight pack for a decision-maker."""

from __future__ import annotations

from typing import Any

from ..models import Target

from .normalize import normalize_items
from .search import build_queries, search_public


class ResearchError(Exception):
    pass


def _hook_lines(items: list[dict[str, Any]], target_name: str, company: str) -> tuple[str, str]:
    """Short hook from top cited item — for asks (no URL in WhatsApp body)."""
    if not items:
        return "", ""
    top = items[0]
    snippet = (top.get("snippet") or top.get("title") or "").strip()
    if len(snippet) > 120:
        snippet = snippet[:117].rstrip() + "…"
    name = target_name or "o alvo"
    comp = company or "a empresa"
    pt = f"Vi material público sobre {comp} ({snippet}) — por isso o timing parece relevante."
    en = f"I saw public material on {comp} ({snippet}) — timing seems relevant."
    if not snippet:
        pt = f"Pesquisei {comp} em fontes públicas antes de pedir sua ajuda com {name}."
        en = f"I looked up {comp} in public sources before asking your help re {name}."
    return pt, en


def research_target(
    target: Target | dict[str, Any],
    *,
    max_items: int = 8,
    max_queries: int = 3,
) -> dict[str, Any]:
    """Return insight pack with cited public snippets. Never invents people."""
    if isinstance(target, Target):
        name = target.name
        company = target.company
        title = target.title
        linkedin_url = target.linkedin_url or ""
    else:
        name = str(target.get("name") or "")
        company = str(target.get("company") or "")
        title = str(target.get("title") or "")
        linkedin_url = str(target.get("linkedin_url") or target.get("linkedin") or "")

    if not (name.strip() or company.strip()):
        raise ResearchError("Nome ou empresa do alvo é obrigatório para pesquisa.")

    queries = build_queries(name, company, title, linkedin_url)
    if not queries:
        raise ResearchError("Não foi possível montar consultas de pesquisa.")

    raw: list[dict[str, str]] = []
    for q in queries[:max_queries]:
        raw.extend(search_public(q, max_results=4))

    items = normalize_items(raw, company=company, max_items=max_items)
    hook_pt, hook_en = _hook_lines(items, name, company)

    return {
        "target": {
            "name": name,
            "company": company,
            "title": title,
            "linkedin_url": linkedin_url,
        },
        "queries": queries[:max_queries],
        "items": items,
        "count": len(items),
        "empty": len(items) == 0,
        "hook_line_pt": hook_pt,
        "hook_line_en": hook_en,
        "source": "public_web_research",
        "note": (
            "Fontes públicas citadas — não inventamos pessoas nem mutuals. "
            "Pontes vêm só da sua rede importada."
            if items
            else "Nenhum resultado público útil — tente nome + empresa mais específicos."
        ),
    }
