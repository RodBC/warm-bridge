"""Strength tutoring — when is it safe to ask this bridge?

Maps strength + mode + confidence to plain-language guidance.
Never invents closeness; uses only fields from the import + scoring.
"""

from __future__ import annotations

from typing import Any

HARD_INTRO_MODES = frozenset({"ask_intro"})
SOFT_MODES = frozenset({"ask_permission", "ask_intel", "peer_forward"})


def strength_advice(
    *,
    strength: str,
    mode: str,
    confidence: str,
    types: list[str],
    bucket: str,
    locale: str = "pt",
) -> dict[str, Any]:
    """Return tutoring payload for UI: level yes | soft | no + headline + bullets."""
    s = (strength or "unknown").lower()
    m = mode or "ask_permission"
    is_direct = bucket == "direct" or "direct" in types

    if is_direct:
        return _pack(
            level="yes",
            can_ask=True,
            locale=locale,
            headline_pt="Você já tem o alvo na rede — pode abordar direto.",
            headline_en="Target is already in your graph — reach out directly.",
            bullets_pt=[
                "Não precisa pedir intro a ninguém.",
                "Use um tom curto e contextual — WhatsApp ou LinkedIn.",
            ],
            bullets_en=[
                "No bridge intro needed.",
                "Keep it short and contextual — WhatsApp or LinkedIn.",
            ],
        )

    if s == "low" or (s == "unknown" and m in HARD_INTRO_MODES and confidence == "low"):
        return _pack(
            level="no",
            can_ask=False,
            locale=locale,
            headline_pt="Ainda não peça intro dura — relação fraca ou fria.",
            headline_en="Don't ask for a hard intro yet — weak or cold tie.",
            bullets_pt=[
                "Prefira pedir mapa (quem decide?) ou permissão leve.",
                "Reaqueça o contato antes de citar o alvo.",
            ],
            bullets_en=[
                "Prefer intel (who decides?) or soft permission.",
                "Re-warm the contact before naming the target.",
            ],
        )

    if m in HARD_INTRO_MODES and s == "high" and confidence in ("high", "medium", "direct"):
        return _pack(
            level="yes",
            can_ask=True,
            locale=locale,
            headline_pt="Sim — confiança alta e caminho claro para intro.",
            headline_en="Yes — high trust and a clear path for an intro.",
            bullets_pt=[
                "Peça uma intro curta com texto pronto para encaminhar.",
                "Dê uma saída fácil se não for o momento.",
            ],
            bullets_en=[
                "Ask for a short intro with a forwardable blurb.",
                "Give them an easy out if timing is off.",
            ],
        )

    if m == "peer_forward" and s in ("high", "medium"):
        return _pack(
            level="soft",
            can_ask=True,
            locale=locale,
            headline_pt="Pode pedir para encaminhar — sem precisar defender a ideia.",
            headline_en="OK to ask them to forward — no need to sell the idea.",
            bullets_pt=[
                "Encaminhar texto é mais leve que pedir intro ativa.",
                "Funciona bem no WhatsApp com relação média/alta.",
            ],
            bullets_en=[
                "Forwarding text is lighter than an active intro.",
                "Works well on WhatsApp with medium/high trust.",
            ],
        )

    if m in SOFT_MODES or s in ("medium", "unknown"):
        return _pack(
            level="soft",
            can_ask=m != "ask_intro",
            locale=locale,
            headline_pt="Pedido leve — mapa, permissão ou encaminhar, não intro dura.",
            headline_en="Soft ask — intel, permission, or forward, not a hard intro.",
            bullets_pt=[
                "Confirme quem decide antes de pedir ponte.",
                "Cite o alvo só se a relação aguentar.",
            ],
            bullets_en=[
                "Confirm who decides before asking for a bridge.",
                "Name the target only if the relationship can handle it.",
            ],
        )

    return _pack(
        level="no",
        can_ask=False,
        locale=locale,
        headline_pt="Espere — fortaleça a relação antes de pedir.",
        headline_en="Hold — strengthen the relationship before asking.",
        bullets_pt=[
            "Adicione notas ou reative o contato.",
            "Tente outra ponte com strength=high.",
        ],
        bullets_en=[
            "Add notes or re-engage the contact.",
            "Try another bridge marked high strength.",
        ],
    )


def attach_tutor(row: dict[str, Any], locale: str = "pt") -> dict[str, Any]:
    """Attach tutor dict to an enriched bridge row (mutates and returns row)."""
    row["tutor"] = strength_advice(
        strength=row.get("strength") or "unknown",
        mode=row.get("mode") or "ask_permission",
        confidence=row.get("confidence") or "low",
        types=row.get("types") or [],
        bucket=row.get("bucket") or "bridge",
        locale=locale,
    )
    return row


def _pack(
    *,
    level: str,
    can_ask: bool,
    locale: str,
    headline_pt: str,
    headline_en: str,
    bullets_pt: list[str],
    bullets_en: list[str],
) -> dict[str, Any]:
    en = locale == "en"
    return {
        "level": level,
        "can_ask": can_ask,
        "headline": headline_en if en else headline_pt,
        "headline_pt": headline_pt,
        "headline_en": headline_en,
        "bullets": bullets_en if en else bullets_pt,
        "bullets_pt": bullets_pt,
        "bullets_en": bullets_en,
    }
