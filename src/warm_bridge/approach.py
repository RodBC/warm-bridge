"""Professional WhatsApp/DM ask templates — clear, respectful, not slangy."""

from __future__ import annotations

from typing import Any

from .models import RankedBridge, Target


TEMPLATES_PT = {
    "ask_intro": (
        "{greeting}\n\n"
        "Estou buscando uma introdução a {target_name} ({target_role}{target_company_bit}).\n"
        "{why_bridge}\n\n"
        "Você poderia fazer uma intro breve? Se preferir, basta encaminhar o texto abaixo:\n\n"
        "{blurb}\n\n"
        "Se o momento não for adequado, sem problema.\n\n"
        "{signoff}"
    ),
    "peer_forward": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Seria possível apenas encaminhar a mensagem a seguir?\n\n"
        "{forward_msg}\n\n"
        "Se preferir não encaminhar, me avise.\n\n"
        "{signoff}"
    ),
    "ask_intel": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Quem conduz a decisão{target_hint} — ainda é {target_name}?\n\n"
        "Não peço introdução agora; só para não abordar a pessoa errada.\n\n"
        "{signoff}"
    ),
    "ask_permission": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Faz sentido eu contactar {target_name} ({target_role}{target_company_bit})?\n\n"
        "Posso mencioná-lo(a) se perguntarem como cheguei — ou prefere que eu não cite?\n\n"
        "{signoff}"
    ),
    "direct": (
        "{greeting}\n\n"
        "{value}\n\n"
        "Haveria disponibilidade para 15 minutos sobre {topic} em {company}?\n"
        "Se não for o contato certo, agradeço se puder indicar a pessoa adequada.\n\n"
        "{signoff}"
    ),
}

TEMPLATES_EN = {
    "ask_intro": (
        "{greeting}\n\n"
        "I am looking for a brief introduction to {target_name} ({target_role}{target_company_bit}).\n"
        "{why_bridge}\n\n"
        "Would you be open to a short intro? Alternatively, feel free to forward:\n\n"
        "{blurb}\n\n"
        "If the timing is not right, I understand.\n\n"
        "{signoff}"
    ),
    "peer_forward": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Could you simply forward the note below?\n\n"
        "{forward_msg}\n\n"
        "If you would rather not, please let me know.\n\n"
        "{signoff}"
    ),
    "ask_intel": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Who owns that decision{target_hint} — is it still {target_name}?\n\n"
        "I am not asking for an introduction yet.\n\n"
        "{signoff}"
    ),
    "ask_permission": (
        "{greeting}\n\n"
        "{why_bridge}\n"
        "Would it be appropriate for me to reach out to {target_name} ({target_role}{target_company_bit})?\n\n"
        "I can mention you if they ask — or leave you out.\n\n"
        "{signoff}"
    ),
    "direct": (
        "{greeting}\n\n"
        "{value}\n\n"
        "Would you have 15 minutes to discuss {topic} at {company}?\n"
        "If you are not the right person, a pointer would help.\n\n"
        "{signoff}"
    ),
}


def _first(name: str) -> str:
    return (name or "").strip().split()[0] if (name or "").strip() else ""


def _why_bridge(bridge: RankedBridge, target: Target, locale: str) -> str:
    types = set(bridge.types)
    company = target.company or ("the company" if locale == "en" else "a empresa")
    if "same_company" in types:
        return (
            f"You appear well connected at {company}."
            if locale == "en"
            else f"Você parece bem conectado(a) na {company}."
        )
    if "mutual_hint" in types:
        return (
            "Based on our notes, you may know them."
            if locale == "en"
            else "Com base nas anotações, você pode conhecê-la."
        )
    if "phone_warm" in types:
        return (
            "Given our working relationship, I wanted to ask you first."
            if locale == "en"
            else "Dada a nossa relação de trabalho, gostaria de pedir sua orientação primeiro."
        )
    if "alumni" in types:
        schools = ", ".join(bridge.contact.get("schools") or []) or (
            "a school" if locale == "en" else "a formação"
        )
        return (
            f"We share background around {schools}."
            if locale == "en"
            else f"Temos trajetória em comum ({schools})."
        )
    if "title_adjacent" in types:
        return (
            "Your role sits close to that function."
            if locale == "en"
            else "Seu cargo fica próximo dessa função."
        )
    return (
        "I thought you might know the right path."
        if locale == "en"
        else "Imaginei que você pudesse indicar o caminho certo."
    )


def _voice(seller: dict, key: str, locale: str, **fmt: str) -> str:
    voice = seller.get("voice") or {}
    locale_key = f"{key}_{locale}"
    raw = voice.get(locale_key) or voice.get(key) or ""
    try:
        return raw.format(**fmt) if raw else ""
    except KeyError:
        return raw


def build_approach(
    seller: dict,
    target: Target,
    bridge: RankedBridge,
    locale: str = "pt",
    insight_hook: str = "",
) -> str:
    idn = seller.get("identity") or {}
    seller_name = idn.get("name") or "Eu"
    company_seller = idn.get("company") or ""
    role_seller = idn.get("role") or ""
    bridge_first = bridge.contact.get("first_name") or _first(bridge.name)
    target_role = target.title or ("decision-maker" if locale == "en" else "tomador de decisão")
    if target.company:
        company_bit = f" @ {target.company}" if locale == "en" else f" · {target.company}"
    else:
        company_bit = ""

    value = _voice(seller, "value_one_liner", locale) or (
        "I help teams buy with less friction."
        if locale == "en"
        else "Trabalho com tecnologia aplicada a life sciences."
    )
    greeting = _voice(seller, "greeting", locale, bridge_first=bridge_first) or (
        f"Hello {bridge_first}," if locale == "en" else f"Olá {bridge_first},"
    )
    signoff = _voice(seller, "signoff", locale) or (
        f"Thank you,\n{seller_name}" if locale == "en" else f"Obrigado,\n{seller_name}"
    )

    mode = "direct" if "direct" in bridge.types else bridge.mode
    templates = TEMPLATES_EN if locale == "en" else TEMPLATES_PT
    tpl = templates[mode]

    if locale == "en":
        seller_bit = seller_name
        if role_seller or company_seller:
            seller_bit += f" ({role_seller}" + (f", {company_seller}" if company_seller else "") + ")"
        blurb = f"{seller_bit}. {value} Would {target.name} be open to 15 minutes?"
        forward_msg = f"Hello {_first(target.name)}, sharing a note from {seller_name}. {value}"
    else:
        seller_bit = seller_name
        if role_seller or company_seller:
            seller_bit += f" ({role_seller}" + (f", {company_seller}" if company_seller else "") + ")"
        blurb = f"{seller_bit}. {value} {target.name} teria 15 minutos para uma conversa?"
        forward_msg = f"Olá {_first(target.name)}, passo o contato de {seller_name}. {value}"

    why = _why_bridge(bridge, target, locale)
    if insight_hook.strip():
        why = f"{why}\n{insight_hook.strip()}"
    target_hint = ""
    if target.company:
        target_hint = f" at {target.company}" if locale == "en" else f" na {target.company}"

    return (
        tpl.format(
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
            topic="talent / people ops" if locale == "en" else "pessoas e talentos",
            company=target.company or ("the company" if locale == "en" else "a empresa"),
        ).strip()
        + "\n"
    )


def approaches_for_ranked(
    seller: dict,
    target: Target,
    ranked: list[RankedBridge],
    locale: str = "pt",
    insight_pack: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    hook = ""
    if insight_pack and not insight_pack.get("empty"):
        hook = (
            insight_pack.get("hook_line_en") or ""
            if locale == "en"
            else insight_pack.get("hook_line_pt") or ""
        )
    out: list[dict[str, Any]] = []
    for b in ranked:
        out.append(
            {
                "contact_id": b.contact_id,
                "name": b.name,
                "score": b.score,
                "types": b.types,
                "mode": "direct" if "direct" in b.types else b.mode,
                "message": build_approach(
                    seller, target, b, locale=locale, insight_hook=hook,
                ),
            }
        )
    return out
