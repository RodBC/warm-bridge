#!/usr/bin/env python3
"""Validate Lead Police pin contract after linkedin-map / find.

Usage:
  # Offline mock (CI)
  WARM_BRIDGE_SELENIUM_MOCK=1 python scripts/validate_board_pins.py

  # After a live map dump:
  python scripts/validate_board_pins.py --json data/out/last_map.json

  # Live smoke (requires Chrome session):
  python scripts/validate_board_pins.py --live

Exit 0 = no critical failures. Enrich misses are warnings unless --strict-photos.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

FAKE_URL_RE = re.compile(r"demo-warmbridge|example\.invalid|acme-example|-mock(?:/|$)", re.I)
PROFILE_URL_RE = re.compile(r"linkedin\.com/(in|pub)/", re.I)
HTTP_RE = re.compile(r"^https?://", re.I)


def _contacts_from_find(find: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for bucket in ("bridges", "direct"):
        for b in find.get(bucket) or []:
            rows.append(b)
    return rows


def _seller_target_pins(find: dict[str, Any], meta: dict[str, Any], seller: dict[str, Any] | None) -> list[dict[str, Any]]:
    pins: list[dict[str, Any]] = []
    identity = (seller or {}).get("identity") or {}
    pins.append(
        {
            "name": identity.get("name") or "seller",
            "linkedin_url": identity.get("linkedin") or meta.get("seller_url") or "",
            "title": identity.get("role") or meta.get("seller_title") or "",
            "company": identity.get("company") or meta.get("seller_company") or "",
            "avatar_url": meta.get("seller_avatar_url") or "",
            "photo": meta.get("seller_avatar_url") or "",
            "_role": "seller",
        }
    )
    tgt = find.get("target") or {}
    pins.append(
        {
            "name": tgt.get("name") or "target",
            "linkedin_url": tgt.get("linkedin_url") or meta.get("target_url") or "",
            "title": tgt.get("title") or meta.get("target_title") or "",
            "company": tgt.get("company") or meta.get("target_company") or "",
            "avatar_url": meta.get("target_avatar_url") or "",
            "photo": meta.get("target_avatar_url") or "",
            "_role": "target",
        }
    )
    return pins


def validate_payload(
    *,
    find: dict[str, Any],
    network: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
    seller: dict[str, Any] | None = None,
    strict_photos: bool = False,
    allow_mock_urls: bool = False,
) -> list[str]:
    """Return list of critical failure strings (empty = pass)."""
    meta = meta or {}
    failures: list[str] = []
    warnings: list[str] = []
    pins = _contacts_from_find(find) + _seller_target_pins(find, meta, seller)

    # Also check raw network contacts (board may show them before find)
    for c in (network or {}).get("contacts") or []:
        pins.append({**c, "_role": "network"})

    enrich_miss = 0
    for p in pins:
        name = (p.get("name") or "").strip()
        role = p.get("_role") or "bridge"
        if not name:
            failures.append(f"[{role}] empty name")
            continue

        url = (p.get("linkedin_url") or "").strip()
        if url and FAKE_URL_RE.search(url) and not allow_mock_urls:
            failures.append(f"[{role}/{name}] fake linkedin_url: {url}")
        elif url and not PROFILE_URL_RE.search(url):
            failures.append(f"[{role}/{name}] linkedin_url not /in/: {url}")
        elif not url and role in ("bridge", "direct", "network"):
            failures.append(f"[{role}/{name}] missing linkedin_url")

        title = (p.get("title") or "").strip()
        company = (p.get("company") or "").strip()
        if role in ("bridge", "direct", "network") and not title and not company:
            # Cap: contacts beyond enrich_cap may lack fields
            failures.append(f"[{role}/{name}] missing title and company")

        avatar = (p.get("avatar_url") or p.get("photo") or "").strip()
        if avatar and not HTTP_RE.match(avatar) and not avatar.startswith("data:"):
            # local /portraits are not happy-path
            if avatar.startswith("/portraits/"):
                warnings.append(f"[{role}/{name}] local portrait fixture (not CDN)")
            else:
                failures.append(f"[{role}/{name}] non-http photo: {avatar}")
        elif not avatar:
            enrich_miss += 1
            warnings.append(f"[{role}/{name}] enrich miss: no avatar_url/photo")

    if strict_photos and enrich_miss:
        failures.append(f"{enrich_miss} pins missing http(s) avatar (strict)")

    for w in warnings:
        print(f"WARN  {w}")
    if not failures:
        print(f"OK    {len(pins)} pins checked · enrich_miss={enrich_miss}")
    return failures


def run_mock() -> list[str]:
    os.environ["WARM_BRIDGE_SELENIUM_MOCK"] = "1"
    from warm_bridge.accounts import build_find_result
    from warm_bridge.linkedin_session.service import map_target
    from warm_bridge.models import load_yaml
    from warm_bridge.models import ROOT as WB_ROOT

    mapped = map_target(
        "https://www.linkedin.com/in/rodrigo-castro-536b85209/",
        {
            "name": "Sabrina Coelho Godoy",
            "linkedin_url": "https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/",
        },
        mock=True,
    )
    seller = load_yaml(WB_ROOT / "profile" / "example.seller.yaml")
    from warm_bridge.models import Target

    target = Target(
        name="Sabrina Coelho Godoy",
        company="3S Checkout",
        title="Analista de Recursos Humanos Pleno",
        linkedin_url="https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/",
    )
    find = build_find_result(
        network=mapped["network"],
        seller=seller,
        target=target,
        locale="pt",
        top_k=8,
        with_approaches=False,
    )
    # Mock uses *-mock URLs — must fail UI contract if treated as real;
    # for offline pipeline we allow_mock_urls but assert no demo-warmbridge.
    for c in mapped["network"].get("contacts") or []:
        url = c.get("linkedin_url") or ""
        if "demo-warmbridge" in url:
            return [f"mock contact exposes demo-warmbridge URL: {url}"]
    return validate_payload(
        find=find,
        network=mapped["network"],
        meta=mapped["meta"],
        seller=seller,
        allow_mock_urls=True,
        strict_photos=False,
    )


def run_live() -> list[str]:
    from warm_bridge.accounts import build_find_result
    from warm_bridge.linkedin_session.service import SeleniumMapError, map_target
    from warm_bridge.models import Target, load_yaml
    from warm_bridge.models import ROOT as WB_ROOT

    try:
        mapped = map_target(
            "https://www.linkedin.com/in/rodrigo-castro-536b85209/",
            {
                "name": "Sabrina Coelho Godoy",
                "linkedin_url": "https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/",
                "company": "3S Checkout",
                "title": "Analista de Recursos Humanos Pleno",
            },
            mock=False,
        )
    except SeleniumMapError as exc:
        return [f"live session gate failed: {exc}"]
    meta = mapped["meta"]
    if int(meta.get("mutual_count") or 0) <= 0:
        return ["live map returned mutual_count=0 — fix Chrome session before UI QA"]

    seller = load_yaml(WB_ROOT / "profile" / "example.seller.yaml")
    identity = dict(seller.get("identity") or {})
    if meta.get("seller_title"):
        identity["role"] = meta["seller_title"]
    if meta.get("seller_company"):
        identity["company"] = meta["seller_company"]
    if meta.get("seller_headline"):
        identity["headline"] = meta["seller_headline"]
    seller = {**seller, "identity": identity}

    target = Target(
        name="Sabrina Coelho Godoy",
        company=meta.get("target_company") or "3S Checkout",
        title=meta.get("target_title") or "Analista de Recursos Humanos Pleno",
        linkedin_url="https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b/",
    )
    find = build_find_result(
        network=mapped["network"],
        seller=seller,
        target=target,
        locale="pt",
        top_k=8,
        with_approaches=False,
    )
    out_dir = WB_ROOT / "data" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    dump = {"network": mapped["network"], "find": find, "meta": meta, "seller": seller}
    (out_dir / "last_map.json").write_text(json.dumps(dump, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out_dir / 'last_map.json'}")
    return validate_payload(
        find=find,
        network=mapped["network"],
        meta=meta,
        seller=seller,
        strict_photos=False,
        allow_mock_urls=False,
    )


def run_json(path: Path, strict_photos: bool) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return validate_payload(
        find=data.get("find") or data,
        network=data.get("network"),
        meta=data.get("meta") or {},
        seller=data.get("seller"),
        strict_photos=strict_photos,
        allow_mock_urls=False,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--live", action="store_true", help="Run live linkedin-map + validate")
    ap.add_argument("--json", type=Path, help="Validate a saved map JSON")
    ap.add_argument("--strict-photos", action="store_true")
    args = ap.parse_args()

    if args.live:
        failures = run_live()
    elif args.json:
        failures = run_json(args.json, args.strict_photos)
    else:
        failures = run_mock()

    for f in failures:
        print(f"FAIL  {f}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
