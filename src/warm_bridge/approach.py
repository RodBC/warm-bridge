from __future__ import annotations

from typing import Any

from .models import RankedBridge, Target


TEMPLATES_PT = {
    "ask_intro": (
        "{greeting}\n\n"
        "Tô tentando chegar na {target_name} ({target_role}{target_company_bit}).\n"
        "{why_bridge}\n\n"
        "Faz sentido te pedir uma intro curta?\n\n"
        "Se ajudar, pode só encaminhar isto:\n\n"
        "— {blurb}\n\n"
        "Se não for o momento, zero problema — me fala.\n\n"
        "{signoff}\n"
    ),
    "peer_forward": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Posso te pedir só pra encaminhar o texto abaixo? Sem precisar defender a ideia.\n\n"
        "—\n{forward_msg}\n—\n\n"
        "Se preferir não encaminhar, me fala que eu parto pra outro caminho.\n\n"
        "{signoff}\n"
    ),
    "ask_intel": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Sabe quem hoje puxa a decisão aí"
        "{target_hint} — ainda é {target_name}, ou mudou?\n\n"
        "Não preciso de intro agora; só queria não bater na porta errada.\n\n"
        "{signoff}\n"
    ),
    "ask_permission": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Estou mapeando se faz sentido eu falar com {target_name}"
        " ({target_role}{target_company_bit}).\n\n"
        "Tudo bem eu te citar como contato da área se perguntarem como te achei "
        "— ou prefere que eu nem mencione?\n\n"
        "{signoff}\n"
    ),
    "direct": (
        "{greeting}\n\n"
        "{value}\n"
        "Faz sentido um papo rápido sobre o fluxo de {topic} em {company}?\n\n"
        "Se não for com você, me aponta a pessoa certa — agradeço.\n\n"
        "{signoff}\n"
    ),
}

TEMPLATES_EN = {
    "ask_intro": (
        "{greeting}\n\n"
        "I'm trying to reach {target_name} ({target_role}{target_company_bit}).\n"
        "{why_bridge}\n\n"
        "Would a short intro make sense?\n\n"
        "If useful, feel free to forward this:\n\n"
        "— {blurb}\n\n"
        "If timing is off, no worries — just say so.\n\n"
        "{signoff}\n"
    ),
    "peer_forward": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Could you forward the note below? No need to champion it.\n\n"
        "—\n{forward_msg}\n—\n\n"
        "If you'd rather not, totally fine — I'll try another path.\n\n"
        "{signoff}\n"
    ),
    "ask_intel": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Do you know who owns that decision today"
        "{target_hint} — still {target_name}, or did it change?\n\n"
        "Not asking for an intro yet; I just don't want to knock on the wrong door.\n\n"
        "{signoff}\n"
    ),
    "ask_permission": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "I'm checking whether it makes sense to reach out to {target_name}"
        " ({target_role}{target_company_bit}).\n\n"
        "OK if I mention you as someone in the space if they ask how I found you "
        "— or prefer I don't?\n\n"
        "{signoff}\n"
    ),
    "direct": (
        "{greeting}\n\n"
        "{value}\n"
        "Would a quick chat about {topic} at {company} be useful?\n\n"
        "If you're not the right person, a pointer helps a lot.\n\n"
        "{signoff}\n"
    ),
}


def _first(name: str) -> str:
    return (name or "").strip().split()[0] if (name or "").strip() else ""


def _why_bridge(bridge: RankedBridge, target: Target, locale: str) -> str:
    types = set(bridge.types)
    company = target.company or "a empresa"
    if "same_company" in types:
        if locale == "en":
            return f"Since you're connected to {company}, you seemed like the right person to ask."
        return f"Como você tem ligação com {company}, achei que fazia sentido te perguntar."
    if "mutual_hint" in types:
        note = (bridge.contact.get("notes") or "").strip()
        if locale == "en":
            return "Your notes pointed at this connection, so I'm asking carefully."
        return "Pelas minhas anotações, você parece ter fio com esse contato — por isso te pergunto com cuidado."
    if "phone_warm" in types:
        if locale == "en":
            return "Given how we usually talk, I wanted to ask you first."
        return "Pelo quanto a gente se fala, quis te pedir antes de ir no frio."
    if "alumni" in types:
        schools = ", ".join(bridge.contact.get("schools") or []) or "a school in common"
        if locale == "en":
            return f"We have {schools} in common, so this is a soft ask."
        return f"A gente tem {schools} em comum, então o pedido é leve."
    if "title_adjacent" in types:
        if locale == "en":
            return "Your role sits close to that buying function."
        return "Seu papel fica perto dessa função de compra."
    if locale == "en":
        return "I thought you might know the path."
    return "Achei que você podia conhecer o caminho."


def _voice(seller: dict, key: str, locale: str, **fmt: str) -> str:
    voice = seller.get("voice") or {}
    locale_key = f"{key}_{locale}"
    raw = voice.get(locale_key) or voice.get(key) or ""
    try:
        return raw.format(**fmt) if raw else ""
    except KeyError:
        return raw


def build_approach(seller: dict, target: Target, bridge: RankedBridge, locale: str = "pt") -> str:
    idn = seller.get("identity") or {}
    seller_name = idn.get("name") or "Eu"
    company_seller = idn.get("company") or ""
    bridge_first = bridge.contact.get("first_name") or _first(bridge.name)
    target_role = target.title or ("decision-maker" if locale == "en" else "tomador de decisão")
    if target.company:
        company_bit = f" @ {target.company}" if locale == "en" else f" na {target.company}"
    else:
        company_bit = ""

    value = _voice(seller, "value_one_liner", locale) or (
        "I help teams buy with less friction." if locale == "en" else "Ajudo times a comprar com menos fricção."
    )
    greeting = _voice(seller, "greeting", locale, bridge_first=bridge_first) or (
        f"Hi {bridge_first}," if locale == "en" else f"Oi {bridge_first},"
    )
    signoff = _voice(seller, "signoff", locale) or (
        f"Thanks,\n{seller_name}" if locale == "en" else f"Valeu,\n{seller_name}"
    )

    # Direct: message the target, not a bridge ask
    mode = "direct" if "direct" in bridge.types else bridge.mode
    templates = TEMPLATES_EN if locale == "en" else TEMPLATES_PT
    tpl = templates[mode]

    blurb = (
        f"{seller_name}"
        + (f" ({company_seller})" if company_seller else "")
        + f". {value} "
        + (
            f"Would like 15 min with {target.name} to understand your process."
            if locale == "en"
            else f"Gostaria de 15 min com {target.name} pra entender o fluxo de vocês."
        )
    )
    forward_msg = (
        f"Hi { _first(target.name) }, sharing {seller_name}'s contact"
        f"{f' ({company_seller})' if company_seller else ''}. {value} "
        f"Thought a quick chat might help."
        if locale == "en"
        else f"Oi {_first(target.name)}, passando contato da {seller_name}"
        f"{f' ({company_seller})' if company_seller else ''}. {value} "
        f"Achei que podia ser útil um papo rápido."
    )

    why = _why_bridge(bridge, target, locale)
    # Avoid redundant why when notes are empty for mutual_hint — still OK

    target_hint = ""
    if target.company:
        target_hint = f" at {target.company}" if locale == "en" else f" na {target.company}"

    topic = "purchasing" if locale == "en" else "compras"

    return tpl.format(
        greeting=greeting,
        signoff=signoff,
        target_name=target.name,
        target_role=target_role,
        target_company_bit=company_bit,
        why_bridge=why,
        blurb=blurb,
        forward_msg=forward_msg,
        target_hint=target_hint,
        value=value,
        topic=topic,
        company=target.company or ("the company" if locale == "en" else "a empresa"),
    ).strip() + "\n"


def approaches_for_ranked(
    seller: dict,
    target: Target,
    ranked: list[RankedBridge],
    locale: str = "pt",
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for b in ranked:
        out.append(
            {
                "contact_id": b.contact_id,
                "name": b.name,
                "score": b.score,
                "types": b.types,
                "mode": "direct" if "direct" in b.types else b.mode,
                "message": build_approach(seller, target, b, locale=locale),
            }
        )
    return out
