"""Offline fixtures when WARM_BRIDGE_SESSION_MOCK=1 — never invents beyond the fixture."""

from __future__ import annotations

from typing import Any


def mock_mutuals(*, empty: bool = False, target_name: str = "Sabrina Coelho Godoy") -> list[dict[str, str]]:
    if empty:
        return []
    return [
        {
            "id": "li_mock_ana",
            "name": "Ana Ribeiro",
            "linkedin_url": "https://www.linkedin.com/in/ana-ribeiro-mock",
            "company": "3S Checkout",
            "title": "Coordenadora de Parcerias",
        },
        {
            "id": "li_mock_bruno",
            "name": "Bruno Martins",
            "linkedin_url": "https://www.linkedin.com/in/bruno-martins-mock",
            "company": "Clínica Horizonte",
            "title": "Gerente Comercial",
        },
        {
            "id": "li_mock_diana",
            "name": "Diana Lopes",
            "linkedin_url": "https://www.linkedin.com/in/diana-lopes-mock",
            "company": "Norte Med",
            "title": "Analista de Compras",
            "avatar_url": "",
        },
    ]


def mock_enrich(contact: dict[str, Any]) -> dict[str, Any]:
    out = dict(contact)
    if not out.get("title") and "ana" in (out.get("name") or "").lower():
        out["title"] = "Coordenadora de Parcerias"
    return out
