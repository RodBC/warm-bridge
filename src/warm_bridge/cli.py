from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .approach import approaches_for_ranked
from .explain import enrich_ranked
from .imports import detect_and_parse, network_from_text
from .models import ROOT, Target, load_yaml
from .paths import find_bridges
from .resolve import resolve_target


def _resolve_network(path: str | None) -> Path:
    if path:
        return Path(path)
    local = ROOT / "data" / "network.yaml"
    if local.exists():
        return local
    return ROOT / "profile" / "example.network.yaml"


def _resolve_seller(path: str | None) -> Path:
    if path:
        return Path(path)
    local = ROOT / "data" / "seller.yaml"
    if local.exists():
        return local
    return ROOT / "profile" / "example.seller.yaml"


def _load_network(path: str | None, text_file: str | None = None) -> dict:
    if text_file:
        raw = Path(text_file).read_text(encoding="utf-8")
        return network_from_text(raw)
    return load_yaml(_resolve_network(path))


def _target_from_args(args: argparse.Namespace) -> Target:
    return Target(
        name=args.target_name,
        company=args.target_company or "",
        title=args.target_title or "",
    )


def cmd_find(args: argparse.Namespace) -> int:
    network = _load_network(args.network, getattr(args, "from_import", None))
    target = _target_from_args(args)
    locale = args.locale or "pt"
    ranked = find_bridges(network, target, top_k=args.top_k)
    enriched = enrich_ranked(ranked, target, locale=locale)
    resolution = resolve_target(network, target)
    payload = {
        "target": target.__dict__,
        "resolution": {
            "status": resolution.status,
            "contact_id": resolution.contact_id,
            "score": resolution.score,
            "rationale": resolution.rationale,
        },
        "bridges": [e for e in enriched if e["bucket"] == "bridge"],
        "direct": [e for e in enriched if e["bucket"] == "direct"],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.out:
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = (target.company or target.name).lower().replace(" ", "-")
        (out_dir / f"{slug}-bridges.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    return 0


def cmd_approach(args: argparse.Namespace) -> int:
    network = _load_network(args.network, getattr(args, "from_import", None))
    seller = load_yaml(_resolve_seller(args.seller))
    target = _target_from_args(args)
    locale = args.locale or (seller.get("targets", {}) or {}).get("locales", ["pt"])[0]
    ranked = find_bridges(network, target, top_k=args.top_k)
    drafts = approaches_for_ranked(seller, target, ranked, locale=locale)
    enriched = enrich_ranked(ranked, target, locale=locale)
    by_id = {e["contact_id"]: e for e in enriched}

    out_dir = Path(args.out or ROOT / "data" / "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = (target.company or target.name).lower().replace(" ", "-")
    for i, d in enumerate(drafts, 1):
        meta = by_id.get(d["contact_id"], {})
        d["path_label"] = meta.get("path_label")
        d["why"] = meta.get("why")
        d["confidence"] = meta.get("confidence")
        msg_path = out_dir / f"{slug}-{i}-{d['contact_id']}.txt"
        header = f"# {meta.get('path_label', d['name'])}\n# confidence={meta.get('confidence')} mode={d['mode']}\n\n"
        msg_path.write_text(header + d["message"], encoding="utf-8")

    (out_dir / f"{slug}-approaches.json").write_text(
        json.dumps({"target": target.__dict__, "locale": locale, "approaches": drafts}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({"locale": locale, "count": len(drafts), "out": str(out_dir)}, indent=2, ensure_ascii=False))
    for d in drafts:
        print("\n---", d.get("path_label") or d["name"], f"(score={d['score']}, mode={d['mode']}) ---")
        print(d["message"])
    return 0


def cmd_import(args: argparse.Namespace) -> int:
    raw = Path(args.file).read_text(encoding="utf-8")
    kind, contacts = detect_and_parse(raw)
    network = {"contacts": contacts}
    out = Path(args.out or ROOT / "data" / "network.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    import yaml

    out.write_text(yaml.safe_dump(network, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(json.dumps({"import_kind": kind, "count": len(contacts), "wrote": str(out)}, indent=2))
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    seller = load_yaml(_resolve_seller(args.seller))
    tutoring = seller.get("sales_tutoring") or {}
    print("## Identity")
    print(_yaml_dump(seller.get("identity") or {}))
    print("## Products")
    for x in tutoring.get("products_sold") or []:
        print(f"- {x}")
    print("## Buyer personas")
    for x in tutoring.get("buyer_personas") or []:
        print(f"- {x}")
    print("## Networking style")
    for x in tutoring.get("networking_style") or []:
        print(f"- {x}")
    print("## Hates doing")
    for x in tutoring.get("hates_doing") or []:
        print(f"- {x}")
    return 0


def cmd_eval(_: argparse.Namespace) -> int:
    cases = load_yaml(ROOT / "evals" / "cases.yaml")["cases"]
    network = load_yaml(ROOT / "profile" / "example.network.yaml")
    failed = 0
    ran = 0
    for case in cases:
        if "target" not in case:
            continue
        ran += 1
        t = case["target"]
        target = Target(name=t["name"], company=t.get("company", ""), title=t.get("title", ""))
        ranked = find_bridges(network, target, top_k=10)
        # Top bridge excluding direct-only self hits when expect_top is a bridge
        bridges_only = [r for r in ranked if "direct" not in r.types]
        by_id = {r.contact_id: r for r in ranked}

        ok = True
        detail = []
        if "expect_top_bridge_id" in case:
            pool = bridges_only or ranked
            top = pool[0].contact_id if pool else None
            if top != case["expect_top_bridge_id"]:
                ok = False
                detail.append(f"top={top} expected={case['expect_top_bridge_id']}")
            if "expect_types_include" in case and pool:
                types = set(pool[0].types)
                need = set(case["expect_types_include"])
                if not need.issubset(types):
                    ok = False
                    detail.append(f"top types={types} need⊆{need}")
        if "expect_bridge_id" in case:
            bid = case["expect_bridge_id"]
            if bid not in by_id:
                ok = False
                detail.append(f"missing bridge {bid}")
            elif "expect_types_include" in case:
                types = set(by_id[bid].types)
                need = set(case["expect_types_include"])
                if not need.issubset(types):
                    ok = False
                    detail.append(f"types={types} need⊆{need}")

        status = "PASS" if ok else "FAIL"
        print(f"{status}  {case['id']}" + (f"  ({'; '.join(detail)})" if detail else ""))
        if not ok:
            failed += 1

    print(f"\n{ran - failed} passed, {failed} failed")
    return 1 if failed else 0


def cmd_serve(_: argparse.Namespace) -> int:
    from .api import run

    run()
    return 0


def _yaml_dump(obj: object) -> str:
    import yaml

    return yaml.safe_dump(obj, sort_keys=False, allow_unicode=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="warm-bridge", description="Warm Bridge CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    def add_target_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--target-name", required=True)
        p.add_argument("--target-company", default="")
        p.add_argument("--target-title", default="")
        p.add_argument("--network", default=None)
        p.add_argument("--from-import", default=None, help="CSV/paste file instead of YAML network")
        p.add_argument("--top-k", type=int, default=None)
        p.add_argument("--locale", default="pt")

    p_f = sub.add_parser("find", help="Rank bridges to a target")
    add_target_args(p_f)
    p_f.add_argument("--out", default=None)
    p_f.set_defaults(func=cmd_find)

    p_a = sub.add_parser("approach", help="Draft approach scripts for top bridges")
    add_target_args(p_a)
    p_a.add_argument("--seller", default=None)
    p_a.add_argument("--out", default=None)
    p_a.set_defaults(func=cmd_approach)

    p_i = sub.add_parser("import", help="Import LinkedIn/phone CSV or paste into data/network.yaml")
    p_i.add_argument("--file", required=True)
    p_i.add_argument("--out", default=None)
    p_i.set_defaults(func=cmd_import)

    p_e = sub.add_parser("eval", help="Run local eval cases")
    p_e.set_defaults(func=cmd_eval)

    p_p = sub.add_parser("profile", help="Show seller / territory tutoring brief")
    p_p.add_argument("--seller", default=None)
    p_p.set_defaults(func=cmd_profile)

    p_s = sub.add_parser("serve", help="Run local FastAPI (UI on :5174 proxies here :8788)")
    p_s.set_defaults(func=cmd_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
