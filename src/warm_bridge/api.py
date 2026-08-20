from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .accounts import build_find_result, find_account
from .imports import detect_and_parse, merge_networks, network_from_text
from .linkedin_session import (
    SeleniumMapError,
    SessionMapError,
    friendly_map_error,
    load_session_config,
    map_target,
    session_status,
)
from .linkedin_session.account.ensure import account_public_config, ensure_session_logged_in
from .models import ROOT, Target, load_yaml
from .outcomes import OutcomeError, validate_events
from .resolve import resolution_as_dict, resolve_target
from .research import ResearchError, research_target

app = FastAPI(title="Warm Bridge API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TargetIn(BaseModel):
    name: str = ""
    company: str = ""
    title: str = ""
    linkedin: str = ""
    linkedin_url: str = ""


class FindRequest(BaseModel):
    target: TargetIn
    network: dict[str, Any] | None = None
    network_text: str | None = None
    seller: dict[str, Any] | None = None
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True
    with_research: bool = False


class ResearchRequest(BaseModel):
    target: TargetIn


class InvestigateRequest(BaseModel):
    target: TargetIn
    network: dict[str, Any] | None = None
    network_text: str | None = None
    seller: dict[str, Any] | None = None
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True
    with_research: bool = True


class ImportRequest(BaseModel):
    text: str
    existing: dict[str, Any] | None = None


class AccountTargetIn(BaseModel):
    id: str = ""
    name: str
    title: str = ""
    linkedin: str = ""


class FindAccountRequest(BaseModel):
    company: str
    targets: list[AccountTargetIn]
    network: dict[str, Any] | None = None
    network_text: str | None = None
    seller: dict[str, Any] | None = None
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True


class LinkedInMapRequest(BaseModel):
    seller_linkedin: str = ""
    target: TargetIn
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True
    seller: dict[str, Any] | None = None
    enrich: bool | None = None


def _target_from_in(t: TargetIn) -> Target:
    from .linkedin import resolve_target_fields

    fields = resolve_target_fields(
        name=t.name,
        company=t.company,
        title=t.title,
        linkedin=t.linkedin_url or t.linkedin or t.name,
    )
    if not fields["name"].strip():
        raise HTTPException(400, "Nome ou link LinkedIn do tomador é obrigatório")
    return Target(
        name=fields["name"],
        company=fields["company"],
        title=fields["title"],
        linkedin_url=fields["linkedin_url"],
    )


def _default_network() -> dict[str, Any]:
    path = ROOT / "data" / "network.yaml"
    if not path.exists():
        path = ROOT / "profile" / "example.network.yaml"
    return load_yaml(path)


def _default_seller() -> dict[str, Any]:
    path = ROOT / "data" / "seller.yaml"
    if not path.exists():
        path = ROOT / "profile" / "example.seller.yaml"
    return load_yaml(path)


def _resolve_network(network: dict[str, Any] | None, network_text: str | None) -> dict[str, Any]:
    if network and network.get("contacts"):
        return network
    if network_text and network_text.strip():
        return network_from_text(network_text)
    return _default_network()


@app.on_event("startup")
def _bootstrap_linkedin_on_startup() -> None:
    """Auto-login from data/secrets/linkedin_account.yaml when configured."""
    try:
        ensure_session_logged_in()
    except Exception:  # noqa: BLE001
        pass


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "product": "warm-bridge"}


@app.get("/api/linkedin-session/status")
def api_linkedin_session_status() -> dict[str, Any]:
    """Structured readiness for live Mapear (Camoufox + profile + secrets)."""
    out = session_status()
    out["account"] = account_public_config()
    return out


@app.get("/api/linkedin-session/account")
def api_linkedin_session_account() -> dict[str, Any]:
    """Public-safe account config (no password)."""
    return account_public_config()


@app.post("/api/linkedin-session/ensure")
def api_linkedin_session_ensure() -> dict[str, Any]:
    """Force session bootstrap from secrets (email OTP / TOTP automated)."""
    try:
        return ensure_session_logged_in(force=True)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, str(exc)) from exc


@app.get("/api/example-seller")
def example_seller() -> dict[str, Any]:
    return load_yaml(ROOT / "profile" / "example.seller.yaml")


@app.get("/api/example-network")
def example_network() -> dict[str, Any]:
    """UI Lead Police demo (Rodrigo→Sabrina). Evals still load example.network.yaml."""
    lead = ROOT / "profile" / "example.lead-police.yaml"
    path = lead if lead.exists() else ROOT / "profile" / "example.network.yaml"
    return load_yaml(path)


@app.get("/api/example-account")
def example_account() -> dict[str, Any]:
    return load_yaml(ROOT / "profile" / "example.account.yaml")


@app.post("/api/find-account")
def api_find_account(req: FindAccountRequest) -> dict[str, Any]:
    if not req.company.strip():
        raise HTTPException(400, "Nome da conta/empresa é obrigatório")
    if not req.targets:
        raise HTTPException(400, "Adicione pelo menos um tomador de decisão")
    network = _resolve_network(req.network, req.network_text)
    seller = req.seller or _default_seller()
    return find_account(
        network=network,
        seller=seller,
        company=req.company,
        targets=[t.model_dump() for t in req.targets],
        locale=req.locale or "pt",
        top_k=req.top_k,
        with_approaches=req.with_approaches,
    )


@app.post("/api/import-network")
def api_import_network(req: ImportRequest) -> dict[str, Any]:
    if not req.text.strip():
        raise HTTPException(400, "Cole o CSV do LinkedIn, CSV do celular, ou cartões de contato.")
    kind, contacts = detect_and_parse(req.text)
    incoming = {"contacts": contacts}
    merged = merge_networks(req.existing or {"contacts": []}, incoming) if req.existing else incoming
    return {
        "import_kind": kind,
        "added": len(contacts),
        "total": len(merged.get("contacts") or []),
        "network": merged,
        "note": (
            "Rede importada por você (Connections.csv, celular ou paste). "
            "Sem login LinkedIn — pontes só do que você trouxe."
        ),
    }


def _maybe_research(target: Target, enabled: bool) -> dict[str, Any] | None:
    if not enabled:
        return None
    try:
        return research_target(target)
    except ResearchError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/research")
def api_research(req: ResearchRequest) -> dict[str, Any]:
    """Public web insight on target/company — cited URLs, no invented people."""
    target = _target_from_in(req.target)
    try:
        return research_target(target)
    except ResearchError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/api/investigate")
def api_investigate(req: InvestigateRequest) -> dict[str, Any]:
    """Find bridges + optional public research — primary wedge API."""
    target = _target_from_in(req.target)
    network = _resolve_network(req.network, req.network_text)
    if not network.get("contacts"):
        raise HTTPException(
            400,
            "Importe sua rede primeiro (Connections.csv, celular ou paste).",
        )
    seller = req.seller or _default_seller()
    insight = _maybe_research(target, req.with_research)
    find = build_find_result(
        network=network,
        seller=seller,
        target=target,
        locale=req.locale or "pt",
        top_k=req.top_k,
        with_approaches=req.with_approaches,
        insight_pack=insight,
    )
    return {"find": find, "insight": insight, "network": network}


@app.post("/api/resolve-target")
def api_resolve_target(payload: dict[str, Any]) -> dict[str, Any]:
    target_raw = payload.get("target") or {}
    try:
        target = _target_from_in(TargetIn(**target_raw))
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"target inválido: {exc}") from exc
    network = _resolve_network(payload.get("network"), payload.get("network_text"))
    return resolution_as_dict(resolve_target(network, target))


@app.post("/api/find")
def api_find(req: FindRequest) -> dict[str, Any]:
    target = _target_from_in(req.target)
    network = _resolve_network(req.network, req.network_text)
    seller = req.seller or _default_seller()
    insight = _maybe_research(target, req.with_research)
    return build_find_result(
        network=network,
        seller=seller,
        target=target,
        locale=req.locale or "pt",
        top_k=req.top_k,
        with_approaches=req.with_approaches,
        insight_pack=insight,
    )


@app.post("/api/linkedin-map")
def api_linkedin_map(req: LinkedInMapRequest, demo: int = 0) -> dict[str, Any]:
    """Seller LinkedIn session → observed mutuals → find pipeline.

    Query `demo=1` or env WARM_BRIDGE_SELENIUM_MOCK=1 uses offline fixture.
    Never silently invents mutuals on driver failure.
    """
    import os

    target = _target_from_in(req.target)
    seller = req.seller or _default_seller()
    if not req.seller_linkedin.strip():
        identity = seller.get("identity") or {}
        seller_li = str(identity.get("linkedin") or "")
        if not seller_li:
            acct = account_public_config()
            seller_li = str(acct.get("linkedin_url") or "")
    else:
        seller_li = req.seller_linkedin.strip()

    use_demo = demo == 1 or os.environ.get("WARM_BRIDGE_SELENIUM_MOCK", "").strip() in (
        "1",
        "true",
        "yes",
    ) or os.environ.get("WARM_BRIDGE_SESSION_MOCK", "").strip() in ("1", "true", "yes")

    if not use_demo:
        try:
            ensure_session_logged_in()
        except Exception:  # noqa: BLE001
            pass
    override: dict[str, Any] = {}
    # Real session: enrich photos by default. Demo/mock skips LinkedIn CDN fetch.
    if req.enrich is not None:
        override["enrich"] = req.enrich
    elif not use_demo:
        override["enrich"] = True
    cfg = load_session_config(override or None)

    try:
        mapped = map_target(
            seller_li,
            {
                "name": target.name,
                "company": target.company,
                "title": target.title,
                "linkedin_url": target.linkedin_url or "",
            },
            cfg,
            mock=True if use_demo else None,
        )
    except SeleniumMapError as exc:
        msg, status = friendly_map_error(exc)
        raise HTTPException(status, msg) from exc

    network = mapped["network"]
    meta = mapped["meta"]

    # Propagate observed seller headline into identity for Lead Police pin cargo.
    identity = dict(seller.get("identity") or {})
    seller_title = str(meta.get("seller_title") or "").strip()
    seller_company = str(meta.get("seller_company") or "").strip()
    seller_headline = str(meta.get("seller_headline") or "").strip()
    if seller_title:
        identity["role"] = seller_title
    if seller_company:
        identity["company"] = seller_company
    if seller_headline:
        identity["headline"] = seller_headline
    elif seller_title and seller_company:
        identity["headline"] = f"{seller_title} - {seller_company}"
    elif seller_title:
        identity["headline"] = seller_title
    if identity:
        seller = {**seller, "identity": identity}

    # Prefer observed target title/company when request fields were empty.
    target_title = str(meta.get("target_title") or "").strip()
    target_company = str(meta.get("target_company") or "").strip()
    if target_title and not (target.title or "").strip():
        target.title = target_title
    if target_company and not (target.company or "").strip():
        target.company = target_company

    find = build_find_result(
        network=network,
        seller=seller,
        target=target,
        locale=req.locale or "pt",
        top_k=req.top_k,
        with_approaches=req.with_approaches,
    )
    return {
        "network": network,
        "find": find,
        "seller": seller,
        "meta": {
            "source": meta.get("source", "linkedin_session"),
            "mutual_count": meta.get("mutual_count", len(network.get("contacts") or [])),
            "mock": bool(meta.get("mock")),
            "enriched": bool(meta.get("enriched")),
            "enrich_cap": meta.get("enrich_cap"),
            "target_avatar_url": meta.get("target_avatar_url") or "",
            "seller_avatar_url": meta.get("seller_avatar_url") or "",
            "target_title": target_title or (target.title or ""),
            "target_company": target_company or (target.company or ""),
            "target_headline": meta.get("target_headline") or "",
            "seller_title": seller_title or str(identity.get("role") or ""),
            "seller_company": seller_company or str(identity.get("company") or ""),
            "seller_headline": str(identity.get("headline") or ""),
        },
    }


@app.post("/api/upload-seller")
async def upload_seller(file: UploadFile = File(...)) -> dict[str, Any]:
    import yaml

    raw = await file.read()
    try:
        data = yaml.safe_load(raw.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(400, f"YAML/JSON inválido: {exc}") from exc
    if not isinstance(data, dict) or "identity" not in data:
        raise HTTPException(400, "Seller precisa do bloco identity")
    return {"ok": True, "seller": data}


@app.post("/api/outcomes")
def api_outcomes(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
    """Validate/echo reach events. Browser localStorage remains source of truth."""
    try:
        events = validate_events(payload)
    except OutcomeError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {"ok": True, "events": events, "note": "Validated only — not persisted on server."}


def run() -> None:
    import uvicorn

    uvicorn.run("warm_bridge.api:app", host="127.0.0.1", port=8788, reload=True)


if __name__ == "__main__":
    run()
