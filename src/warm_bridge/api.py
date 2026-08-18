from __future__ import annotations

from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .approach import approaches_for_ranked
from .explain import enrich_ranked
from .imports import detect_and_parse, merge_networks, network_from_text
from .models import ROOT, Target, load_yaml
from .paths import find_bridges
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
    locale = req.locale or "pt"

    resolution = resolve_target(network, target)
    ranked = find_bridges(network, target, top_k=req.top_k)
    enriched = enrich_ranked(ranked, target, locale=locale)

    bridges = [e for e in enriched if e["bucket"] == "bridge"]
    directs = [e for e in enriched if e["bucket"] == "direct"]

    approaches: list[dict[str, Any]] = []
    if req.with_approaches and ranked:
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
        "proof_line": _proof_line(bridges, directs, target, locale),
        "note": (
            "Você envia a mensagem. O produto é achar a ponte + o pedido certo — "
            "não disparar spam pela sua rede."
        ),
    }


def _proof_line(
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


def run() -> None:
    import uvicorn

    uvicorn.run("warm_bridge.api:app", host="127.0.0.1", port=8788, reload=True)


if __name__ == "__main__":
    run()
