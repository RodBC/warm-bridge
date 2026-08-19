from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .accounts import build_find_result, find_account
from .imports import detect_and_parse, merge_networks, network_from_text
from .models import ROOT, Target, load_yaml
from .outcomes import OutcomeError, validate_events
from .resolve import resolution_as_dict, resolve_target

app = FastAPI(title="Warm Bridge API", version="0.2.0")

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
    name: str
    company: str = ""
    title: str = ""


class FindRequest(BaseModel):
    target: TargetIn
    network: dict[str, Any] | None = None
    network_text: str | None = None
    seller: dict[str, Any] | None = None
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True


class ImportRequest(BaseModel):
    text: str
    existing: dict[str, Any] | None = None


class AccountTargetIn(BaseModel):
    id: str = ""
    name: str
    title: str = ""


class FindAccountRequest(BaseModel):
    company: str
    targets: list[AccountTargetIn]
    network: dict[str, Any] | None = None
    network_text: str | None = None
    seller: dict[str, Any] | None = None
    locale: str = "pt"
    top_k: int = 8
    with_approaches: bool = True


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


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "product": "warm-bridge"}


@app.get("/api/example-seller")
def example_seller() -> dict[str, Any]:
    return load_yaml(ROOT / "profile" / "example.seller.yaml")


@app.get("/api/example-network")
def example_network() -> dict[str, Any]:
    return load_yaml(ROOT / "profile" / "example.network.yaml")


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
            "Dados que você colou/importou. Warm Bridge não scrapa LinkedIn nem agenda. "
            "Exporte Connections.csv no próprio LinkedIn ou cole contatos que você já tem."
        ),
    }


@app.post("/api/resolve-target")
def api_resolve_target(payload: dict[str, Any]) -> dict[str, Any]:
    target_raw = payload.get("target") or {}
    if not (target_raw.get("name") or "").strip():
        raise HTTPException(400, "target.name obrigatório")
    target = Target(
        name=target_raw["name"],
        company=target_raw.get("company") or "",
        title=target_raw.get("title") or "",
    )
    network = _resolve_network(payload.get("network"), payload.get("network_text"))
    return resolution_as_dict(resolve_target(network, target))


@app.post("/api/find")
def api_find(req: FindRequest) -> dict[str, Any]:
    if not req.target.name.strip():
        raise HTTPException(400, "Nome do tomador de decisão é obrigatório")
    network = _resolve_network(req.network, req.network_text)
    seller = req.seller or _default_seller()
    target = Target(name=req.target.name, company=req.target.company, title=req.target.title)
    return build_find_result(
        network=network,
        seller=seller,
        target=target,
        locale=req.locale or "pt",
        top_k=req.top_k,
        with_approaches=req.with_approaches,
    )


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
