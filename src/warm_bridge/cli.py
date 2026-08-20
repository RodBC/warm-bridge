from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .accounts import build_find_result, find_account
from .approach import approaches_for_ranked
from .explain import enrich_ranked
from .imports import detect_and_parse, network_from_text
from .models import ROOT, Target, load_yaml
from .outcomes import ALLOWED_STATUSES, OutcomeError, normalize_event
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
    resolution = resolve_target(network, target)
    payload = build_find_result(
        network=network,
        seller=load_yaml(_resolve_seller(args.seller)),
        target=target,
        locale=locale,
        top_k=args.top_k or 8,
        with_approaches=False,
    )
    payload["resolution"] = {
        "status": resolution.status,
        "contact_id": resolution.contact_id,
        "score": resolution.score,
        "rationale": resolution.rationale,
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

        if "expect_tutor_level" in case and "expect_bridge_id" in case:
            bid = case["expect_bridge_id"]
            if bid in by_id:
                enriched = enrich_ranked([by_id[bid]], target, locale="pt")
                level = enriched[0].get("tutor", {}).get("level")
                if level != case["expect_tutor_level"]:
                    ok = False
                    detail.append(f"tutor level={level} expected={case['expect_tutor_level']}")

        if case.get("check") == "mode_high_trust_intro":
            ana = by_id.get("c_ana")
            if not ana or ana.mode not in ("ask_intro", "peer_forward"):
                ok = False
                detail.append(f"c_ana mode={getattr(ana, 'mode', None)}")
            elif ana:
                enriched = enrich_ranked([ana], target, locale="pt")
                if enriched[0].get("tutor", {}).get("level") != "yes":
                    ok = False
                    detail.append("c_ana tutor not yes")

        if case.get("check") == "mode_low_trust_soft":
            edu = by_id.get("c_edu")
            if not edu or edu.mode in ("ask_intro",):
                ok = False
                detail.append(f"c_edu mode={getattr(edu, 'mode', None)}")
            elif edu:
                enriched = enrich_ranked([edu], target, locale="pt")
                if enriched[0].get("tutor", {}).get("level") not in ("soft", "no"):
                    ok = False
                    detail.append(f"c_edu tutor={enriched[0].get('tutor', {}).get('level')}")

        if case.get("check") == "account_multi_target":
            account = load_yaml(ROOT / "profile" / "example.account.yaml")
            seller = load_yaml(ROOT / "profile" / "example.seller.yaml")
            out = find_account(
                network=network,
                seller=seller,
                company=account["company"],
                targets=account["targets"],
                locale="pt",
                with_approaches=False,
            )
            if out["total_targets"] < 2:
                ok = False
                detail.append(f"targets={out['total_targets']}")
            if out["with_path"] < 2:
                ok = False
                detail.append(f"with_path={out['with_path']}")

        if case.get("check") == "outcome_statuses":
            sample = {
                "targetName": "Marina Costa",
                "bridgeId": "c_ana",
                "bridgeName": "Ana Souza",
                "status": "sent",
            }
            try:
                normalized = normalize_event(sample)
                if normalized["status"] not in ALLOWED_STATUSES:
                    ok = False
                    detail.append("normalized status not allowed")
            except OutcomeError as exc:
                ok = False
                detail.append(f"valid event rejected: {exc}")
            try:
                normalize_event({**sample, "status": "invented_reply"})
                ok = False
                detail.append("invented status accepted")
            except OutcomeError:
                pass
            if "copied" not in ALLOWED_STATUSES or "intro_landed" not in ALLOWED_STATUSES:
                ok = False
                detail.append("missing core statuses")

        if case.get("check") == "linkedin_slug_resolve":
            from .linkedin import display_name_from_linkedin, linkedin_slug, normalize_linkedin_url
            from .resolve import resolve_target

            url = "https://www.linkedin.com/in/marina-costa-acme-example"
            if linkedin_slug(url) != "marina-costa-acme-example":
                ok = False
                detail.append(f"slug={linkedin_slug(url)}")
            if not normalize_linkedin_url("linkedin.com/in/ana-ribeiro-acme-example"):
                ok = False
                detail.append("normalize failed")
            guessed = display_name_from_linkedin(url)
            if not guessed or "Marina" not in guessed:
                ok = False
                detail.append(f"guess={guessed}")
            res = resolve_target(
                network,
                Target(
                    name="Marina Costa",
                    company="Acme Saúde",
                    linkedin_url=url,
                ),
            )
            if res.status != "CONFIRMED" or res.contact_id != "c_marina":
                ok = False
                detail.append(f"resolve={res.status}/{res.contact_id}")

        if case.get("check") == "linkedin_map_mock":
            from .linkedin_session import map_target

            seller = load_yaml(ROOT / "profile" / "example.seller.yaml")
            tname = "Sabrina Coelho Godoy"
            mapped = map_target(
                "https://www.linkedin.com/in/rodrigo-castro-536b85209",
                {
                    "name": tname,
                    "company": "3S Checkout",
                    "title": "Head de Parcerias",
                    "linkedin_url": "https://www.linkedin.com/in/sabrina-coelho-godoy-98094917b",
                },
                mock=True,
                mock_empty=False,
            )
            if not mapped["network"]["contacts"]:
                ok = False
                detail.append("mock mutuals empty")
            find = build_find_result(
                network=mapped["network"],
                seller=seller,
                target=Target(name=tname, company="3S Checkout", title="Head de Parcerias"),
                locale="pt",
                with_approaches=False,
            )
            if not find["bridges"]:
                ok = False
                detail.append("expected non-empty bridges from mock mutuals")
            empty_mapped = map_target(
                "https://www.linkedin.com/in/rodrigo-castro-536b85209",
                {"name": tname, "company": "3S Checkout"},
                mock=True,
                mock_empty=True,
            )
            empty_find = build_find_result(
                network=empty_mapped["network"],
                seller=seller,
                target=Target(name=tname, company="3S Checkout"),
                locale="pt",
                with_approaches=False,
            )
            if empty_find["bridges"] or empty_find["direct"]:
                ok = False
                detail.append("empty mock fabricated bridges")

        if case.get("check") == "otp_parse_linkedin_email":
            from .linkedin_session.otp_inbox.parse import extract_otp

            if extract_otp("Your LinkedIn verification code is 482910. Do not share.") != "482910":
                ok = False
                detail.append("en parse failed")
            if extract_otp("Seu código de verificação LinkedIn: 739201") != "739201":
                ok = False
                detail.append("pt parse failed")
            if extract_otp("no code here"):
                ok = False
                detail.append("false positive")
            # Year-like 20xxxx in footers must not win over real OTP
            year_footer = (
                "Your LinkedIn verification code is 482910.\n"
                "© LinkedIn Corporation 202603"
            )
            if extract_otp(year_footer) != "482910":
                ok = False
                detail.append(f"year filter failed: {extract_otp(year_footer)}")
            if extract_otp("Copyright 202603 LinkedIn") is not None:
                ok = False
                detail.append("year-only false positive")

        if case.get("check") == "challenge_classifier":
            from .linkedin_session.burner.bootstrap import detect_challenge_from_text

            fixtures = [
                (
                    "email_otp_en",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Enter the code we emailed you. Verification code",
                    "email_otp",
                ),
                (
                    "email_otp_pt",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Enviamos um código. Digite o código de verificação. Verifique seu e-mail",
                    "email_otp",
                ),
                (
                    "captcha_with_otp",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Security verification. Unusual activity. Enter the code",
                    "email_otp",
                ),
                (
                    "captcha_only",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Security verification. Unusual activity. Solve this captcha",
                    "captcha",
                ),
                (
                    "sms_guard",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Enter the code we texted to your phone via SMS mobile",
                    "sms",
                ),
                (
                    "no_bare_sms",
                    "https://www.linkedin.com/login",
                    "Sign in to LinkedIn. Email or phone. Password.",
                    "none",
                ),
                (
                    "totp",
                    "https://www.linkedin.com/checkpoint/challenge/",
                    "Open your authenticator app and enter the code from your authenticator",
                    "totp",
                ),
                (
                    "bad_creds",
                    "https://www.linkedin.com/login",
                    "Wrong email or password. That's not the right password.",
                    "bad_creds",
                ),
            ]
            for fid, url, body, expect in fixtures:
                got = detect_challenge_from_text(url=url, body=body)
                if got != expect:
                    ok = False
                    detail.append(f"{fid}: got={got} expected={expect}")

        if case.get("check") == "session_status_structure":
            from .linkedin_session import session_status

            st = session_status()
            for key in ("ready", "blockers", "hints", "checks", "severity"):
                if key not in st:
                    ok = False
                    detail.append(f"missing {key}")
            checks = st.get("checks") or {}
            for ck in (
                "backend",
                "camoufox_importable",
                "profile_dir_exists",
                "burner_secrets_present",
                "mock_mode",
                "logged_in_hint",
            ):
                if ck not in checks:
                    ok = False
                    detail.append(f"checks missing {ck}")

        if case.get("check") == "app_password_preflight":
            from .linkedin_session.burner.secrets import (
                AccountSecrets,
                looks_like_gmail_app_password,
                validate_secrets_for_bootstrap,
            )

            if not looks_like_gmail_app_password("abcd efgh ijkl mnop"):
                ok = False
                detail.append("spaced app password rejected")
            if looks_like_gmail_app_password("Linked123!@#"):
                ok = False
                detail.append("normal password accepted")
            try:
                validate_secrets_for_bootstrap(
                    AccountSecrets(
                        email="a@b.com",
                        password="x",
                        gmail_app_password="Linked123!@#",
                    )
                )
                ok = False
                detail.append("preflight accepted normal password")
            except ValueError:
                pass
            try:
                validate_secrets_for_bootstrap(
                    AccountSecrets(
                        email="a@b.com",
                        password="x",
                        gmail_app_password="abcdefghijklmnop",
                    )
                )
            except ValueError as exc:
                ok = False
                detail.append(f"valid app password rejected: {exc}")
        if case.get("check") == "research_pack_structure":
            from .research.normalize import normalize_items
            from .research.search import build_queries
            from .research.service import research_target

            items = normalize_items(
                [
                    {
                        "title": "Acme Saúde expands hiring",
                        "url": "https://example.com/acme-news",
                        "snippet": "Acme Saúde announced new roles.",
                    },
                ],
                company="Acme Saúde",
            )
            if not items or not items[0].get("url"):
                ok = False
                detail.append("normalize_items empty")
            qs = build_queries("Marina Costa", "Acme Saúde", "Diretora de Compras")
            if len(qs) < 2:
                ok = False
                detail.append(f"queries={qs}")
            # Structure without live search (may be empty in sandbox)
            pack = research_target(
                Target(name="Marina Costa", company="Acme Saúde", title="Diretora"),
                max_queries=1,
                max_items=4,
            )
            for key in ("items", "queries", "empty", "source", "note"):
                if key not in pack:
                    ok = False
                    detail.append(f"missing {key}")
            if pack.get("source") != "public_web_research":
                ok = False
                detail.append(f"source={pack.get('source')}")
            find = build_find_result(
                network=network,
                seller=load_yaml(ROOT / "profile" / "example.seller.yaml"),
                target=Target(name="Marina Costa", company="Acme Saúde"),
                locale="pt",
                with_approaches=True,
                insight_pack=pack,
            )
            if "insight" not in find:
                ok = False
                detail.append("find missing insight")
            if find["bridges"] and not find["bridges"][0].get("message"):
                ok = False
                detail.append("approach missing with insight")

        status = "PASS" if ok else "FAIL"
        print(f"{status}  {case['id']}" + (f"  ({'; '.join(detail)})" if detail else ""))
        if not ok:
            failed += 1

    print(f"\n{ran - failed} passed, {failed} failed")
    return 1 if failed else 0


def cmd_linkedin_map(args: argparse.Namespace) -> int:
    """Map mutuals via LinkedIn session (or mock) → find JSON."""
    import os

    from .linkedin_session import SeleniumMapError, load_session_config, map_target

    seller_li = args.seller_linkedin or ""
    seller = load_yaml(_resolve_seller(args.seller))
    if not seller_li:
        seller_li = str((seller.get("identity") or {}).get("linkedin") or "")

    target_name = args.target_name or ""
    target_url = args.target_url or ""
    if not target_name and not target_url:
        print("error: --target-name or --target-url required", file=sys.stderr)
        return 2

    use_mock = bool(args.mock) or os.environ.get("WARM_BRIDGE_SELENIUM_MOCK", "").strip() in (
        "1",
        "true",
        "yes",
    )
    cfg = load_session_config({"enrich": bool(args.enrich)} if args.enrich else None)
    try:
        mapped = map_target(
            seller_li,
            {
                "name": target_name,
                "company": args.target_company or "",
                "title": args.target_title or "",
                "linkedin_url": target_url or target_name,
            },
            cfg,
            mock=True if use_mock else None,
            mock_empty=bool(args.mock_empty),
        )
    except SeleniumMapError as exc:
        print(json.dumps({"error": str(exc), "status": exc.status}, ensure_ascii=False), file=sys.stderr)
        return 1

    from .linkedin import resolve_target_fields

    fields = resolve_target_fields(
        name=target_name,
        company=args.target_company or "",
        title=args.target_title or "",
        linkedin=target_url or target_name,
    )
    target = Target(
        name=fields["name"],
        company=fields["company"],
        title=fields["title"],
        linkedin_url=fields["linkedin_url"],
    )
    find = build_find_result(
        network=mapped["network"],
        seller=seller,
        target=target,
        locale=args.locale or "pt",
        top_k=args.top_k or 8,
        with_approaches=bool(args.with_approaches),
    )
    payload = {
        "network": mapped["network"],
        "find": find,
        "meta": {
            "source": "linkedin_session",
            "mutual_count": mapped["meta"].get("mutual_count", 0),
            "mock": bool(mapped["meta"].get("mock")),
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_burner_login(args: argparse.Namespace) -> int:
    """Ops-only: bootstrap product burner LinkedIn session via Camoufox + Gmail OTP."""
    from .linkedin_session.burner.bootstrap import bootstrap_burner_session

    try:
        result = bootstrap_burner_session(headed=not args.headless)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def cmd_session_login(args: argparse.Namespace) -> int:
    """Open headed Camoufox with seller profile — manual LinkedIn login/2FA."""
    from .linkedin_session.config import load_session_config
    from .linkedin_session.driver.camoufox import build_camoufox, quit_browser

    cfg = load_session_config()
    session = build_camoufox(cfg, headless=False)
    page = session.browser_page
    page.get("https://www.linkedin.com/login")
    print(
        "Camoufox aberto — faça login no LinkedIn e complete 2FA manualmente. "
        "Pressione Enter aqui quando terminar.",
        file=sys.stderr,
    )
    try:
        input()
    except EOFError:
        pass
    quit_browser(session)
    print(json.dumps({"status": "closed", "profile_dir": cfg.profile_dir}, ensure_ascii=False))
    return 0


def cmd_session_status(_: argparse.Namespace) -> int:
    from .linkedin_session import session_status

    print(json.dumps(session_status(), indent=2, ensure_ascii=False))
    return 0


def cmd_gmail_auth(_: argparse.Namespace) -> int:
    """Ops-only: one-time Gmail OAuth for burner OTP inbox."""
    from .linkedin_session.burner.gmail_otp import get_gmail_service
    from .linkedin_session.burner.secrets import load_burner_secrets

    try:
        sec = load_burner_secrets()
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    if not sec.gmail_credentials_json or not sec.gmail_token_json:
        print("error: gmail paths missing in burner yaml", file=sys.stderr)
        return 2
    get_gmail_service(
        credentials_json=sec.gmail_credentials_json,
        token_json=sec.gmail_token_json,
    )
    print(json.dumps({"status": "gmail_oauth_ok", "token": str(sec.gmail_token_json)}, ensure_ascii=False))
    return 0


def cmd_serve(_: argparse.Namespace) -> int:
    from .api import run

    run()
    return 0


def cmd_research(args: argparse.Namespace) -> int:
    from .research import ResearchError, research_target

    target = Target(
        name=args.target_name,
        company=args.target_company or "",
        title=args.target_title or "",
        linkedin_url=args.target_linkedin or "",
    )
    try:
        pack = research_target(target)
    except ResearchError as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(pack, indent=2, ensure_ascii=False))
    return 0


def cmd_investigate(args: argparse.Namespace) -> int:
    from .research import ResearchError, research_target

    network = _load_network(args.network, getattr(args, "from_import", None))
    if not network.get("contacts"):
        print("error: network empty — import Connections.csv first", file=sys.stderr)
        return 2
    seller = load_yaml(_resolve_seller(args.seller))
    target = _target_from_args(args)
    locale = args.locale or "pt"
    insight = None
    if not args.no_research:
        try:
            insight = research_target(target)
        except ResearchError as exc:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
            return 1
    find = build_find_result(
        network=network,
        seller=seller,
        target=target,
        locale=locale,
        top_k=args.top_k or 8,
        with_approaches=bool(args.with_approaches),
        insight_pack=insight,
    )
    print(
        json.dumps(
            {"find": find, "insight": insight, "network": network},
            indent=2,
            ensure_ascii=False,
        )
    )
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
    p_f.add_argument("--seller", default=None)
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

    p_li = sub.add_parser(
        "linkedin-map",
        help="Map mutuals via LinkedIn Camoufox session (or --mock) → find JSON",
    )
    p_li.add_argument("--seller-linkedin", default="")
    p_li.add_argument("--seller", default=None)
    p_li.add_argument("--target-name", default="")
    p_li.add_argument("--target-url", default="", help="Target LinkedIn profile URL")
    p_li.add_argument("--target-company", default="")
    p_li.add_argument("--target-title", default="")
    p_li.add_argument("--locale", default="pt")
    p_li.add_argument("--top-k", type=int, default=8)
    p_li.add_argument("--with-approaches", action="store_true", default=True)
    p_li.add_argument("--no-approaches", action="store_false", dest="with_approaches")
    p_li.add_argument("--mock", action="store_true", help="Use offline mutuals fixture")
    p_li.add_argument("--mock-empty", action="store_true", help="Mock returns zero mutuals")
    p_li.add_argument("--enrich", action="store_true", help="Optional profile enrich pass")
    p_li.set_defaults(func=cmd_linkedin_map)

    p_bl = sub.add_parser(
        "burner-login",
        help="Ops-only: product burner login + Gmail OTP / TOTP (Layer 5)",
    )
    p_bl.add_argument("--headless", action="store_true", help="Headless Camoufox (not recommended)")
    p_bl.set_defaults(func=cmd_burner_login)

    p_sl = sub.add_parser(
        "session-login",
        help="Open headed Camoufox for seller manual LinkedIn login/2FA",
    )
    p_sl.set_defaults(func=cmd_session_login)

    p_ss = sub.add_parser("session-status", help="Print LinkedIn session readiness JSON")
    p_ss.set_defaults(func=cmd_session_status)

    p_ga = sub.add_parser(
        "gmail-auth",
        help="Ops-only: one-time Gmail OAuth for burner OTP inbox",
    )
    p_ga.set_defaults(func=cmd_gmail_auth)

    p_r = sub.add_parser("research", help="Public web insight on target/company")
    p_r.add_argument("--target-name", required=True)
    p_r.add_argument("--target-company", default="")
    p_r.add_argument("--target-title", default="")
    p_r.add_argument("--target-linkedin", default="")
    p_r.set_defaults(func=cmd_research)

    p_inv = sub.add_parser("investigate", help="Find bridges + public research (owned graph)")
    add_target_args(p_inv)
    p_inv.add_argument("--seller", default=None)
    p_inv.add_argument("--no-research", action="store_true")
    p_inv.add_argument("--with-approaches", action="store_true", default=True)
    p_inv.add_argument("--no-approaches", action="store_false", dest="with_approaches")
    p_inv.set_defaults(func=cmd_investigate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
