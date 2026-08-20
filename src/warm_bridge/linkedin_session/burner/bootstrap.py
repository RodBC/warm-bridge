"""Ops-only LinkedIn login + OTP bootstrap (Career Fit state machine port).

Never expose password fields in public API/UI. Secrets from data/secrets only.
"""

from __future__ import annotations

import time
from typing import Any

from ..config import SessionConfig, load_session_config
from ..driver.camoufox import launch_persistent, new_page
from .gmail_otp import wait_for_linkedin_otp
from .secrets import AccountSecrets, load_account_secrets, validate_secrets_for_bootstrap
from .totp import generate_totp

LINKEDIN_LOGIN = "https://www.linkedin.com/login"


def _body_lower(page: Any, n: int = 2500) -> str:
    try:
        return (page.locator("body").inner_text(timeout=4000) or "").lower()[:n]
    except Exception:  # noqa: BLE001
        return ""


def detect_challenge_from_text(*, url: str = "", body: str = "") -> str:
    """Classify challenge from URL + visible body (PT/EN).

    Returns: email_otp | totp | sms | none | captcha | bad_creds
    """
    u = (url or "").lower()
    head = (body or "").lower()

    if "captcha" in head or "unusual activity" in head or "security verification" in head:
        if any(
            x in head
            for x in (
                "enter the code",
                "verification code",
                "código de verificação",
                "digite o código",
                "pin",
            )
        ):
            return "email_otp"
        return "captcha"

    # SMS only when phone + text/sms/mobile (avoid bare "sms" false positives)
    if "phone" in head and ("text" in head or "sms" in head or "mobile" in head):
        return "sms"
    if "telefone" in head and (
        "mensagem de texto" in head or "sms" in head or "celular" in head
    ):
        return "sms"

    if any(
        x in head
        for x in (
            "authenticator",
            "verification app",
            "google authenticator",
            "enter the code from your authenticator",
            "autenticador",
            "aplicativo de autenticação",
        )
    ):
        return "totp"

    if any(
        x in head
        for x in (
            "enter the code",
            "verification code",
            "we emailed you",
            "email you a code",
            "check your email",
            "código de verificação",
            "digite o código",
            "enviamos um código",
            "verifique seu e-mail",
            "verifique seu email",
            "pin",
        )
    ) or "challenge" in u:
        return "email_otp"

    if any(
        x in head
        for x in (
            "wrong email or password",
            "couldn’t find a linkedin account",
            "couldn't find a linkedin account",
            "that's not the right password",
            "incorrect password",
            "e-mail ou senha incorretos",
            "email ou senha incorretos",
            "senha incorreta",
        )
    ):
        return "bad_creds"

    return "none"


def _detect_challenge(page: Any) -> str:
    return detect_challenge_from_text(url=page.url or "", body=_body_lower(page))


def _first_visible(page: Any, selector: str):
    loc = page.locator(selector)
    n = loc.count()
    for i in range(n):
        el = loc.nth(i)
        try:
            if el.is_visible():
                return el
        except Exception:  # noqa: BLE001
            continue
    return loc.first if n else None


def _fill_credentials(page: Any, secrets: AccountSecrets) -> None:
    time.sleep(1.0)
    email_el = _first_visible(page, "input[type='email'], #username, input[name='session_key']")
    if email_el is None:
        raise RuntimeError("LinkedIn login: campo de email não encontrado")
    email_el.click(timeout=5000, force=True)
    email_el.fill(secrets.email, timeout=5000, force=True)

    pw_el = _first_visible(
        page, "input[type='password'], #password, input[name='session_password']"
    )
    if pw_el is None:
        raise RuntimeError("LinkedIn login: campo de senha não encontrado")
    pw_el.click(timeout=5000, force=True)
    pw_el.fill(secrets.password, timeout=5000, force=True)

    time.sleep(0.5)
    clicked = False
    for name in ("Entrar", "Sign in", "Sign In"):
        try:
            btn = page.get_by_role("button", name=name)
            for i in range(btn.count()):
                el = btn.nth(i)
                if el.is_visible():
                    el.click(timeout=5000)
                    clicked = True
                    break
            if clicked:
                break
        except Exception:  # noqa: BLE001
            continue
    if not clicked:
        for sel in (
            "button[type='submit']",
            "button[data-litms-control-urn*='login']",
            "button.btn__primary--large",
        ):
            btn = _first_visible(page, sel)
            if btn is None:
                continue
            try:
                btn.click(timeout=5000)
                clicked = True
                break
            except Exception:  # noqa: BLE001
                continue
    if not clicked:
        pw_el.press("Enter")
    time.sleep(1.0)


def _fill_otp(page: Any, code: str) -> None:
    for sel in (
        "input[name='pin']",
        "input#input__email_verification_pin",
        "input[id*='verification']",
        "input[autocomplete='one-time-code']",
        "input[type='tel']",
        "input[type='text']",
    ):
        try:
            loc = page.locator(sel)
            if loc.count():
                loc.first.fill(code, timeout=5000)
                break
        except Exception:  # noqa: BLE001
            continue
    for sel in (
        "button[type='submit']",
        "button[data-id='sign-in-form__submit-btn']",
        "button.form__submit",
    ):
        try:
            loc = page.locator(sel)
            if loc.count():
                loc.first.click(timeout=5000)
                return
        except Exception:  # noqa: BLE001
            continue
    page.keyboard.press("Enter")


def authed_url(url: str) -> bool:
    """True when URL looks like an authenticated LinkedIn surface."""
    u = (url or "").lower()
    if any(x in u for x in ("/login", "/uas/", "/checkpoint", "/authwall")):
        return False
    return any(x in u for x in ("/feed", "/in/", "/jobs", "/mynetwork", "/messaging"))


def _wait_feed(page: Any, *, timeout_sec: float = 90) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if authed_url(page.url or ""):
            return True
        time.sleep(2)
    return False


def _await_post_password(page: Any, *, timeout_sec: float = 45) -> str:
    """After password submit, wait until challenge / feed / error appears."""
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        if authed_url(page.url or ""):
            return "none"
        ch = _detect_challenge(page)
        if ch != "none":
            return ch
        time.sleep(1.5)
    return _detect_challenge(page)


def bootstrap_burner_session(
    secrets: AccountSecrets | None = None,
    *,
    headed: bool = False,
    timeout_sec: float = 120,
) -> dict[str, Any]:
    return bootstrap_account_session(
        secrets=secrets,
        headed=headed,
        timeout_sec=timeout_sec,
    )


def bootstrap_account_session(
    secrets: AccountSecrets | None = None,
    *,
    headed: bool = False,
    timeout_sec: float = 120,
    cfg: SessionConfig | None = None,
) -> dict[str, Any]:
    """Camoufox login + OTP → persist profile. Ops-only. Never call from public API."""
    sec = secrets or load_account_secrets()
    validate_secrets_for_bootstrap(sec)

    profile_dir = sec.profile_dir or str(load_session_config().profile_dir)
    session_cfg = cfg or SessionConfig(
        profile_dir=profile_dir,
        user_data_dir=profile_dir,
        backend="camoufox",
        headless=not headed,
    )
    if not session_cfg.profile_dir:
        session_cfg.profile_dir = profile_dir
        session_cfg.user_data_dir = profile_dir

    final_url = ""
    challenge = "none"
    logged_in = False
    otp_timeout = max(30.0, timeout_sec)

    with launch_persistent(session_cfg, headless=not headed) as context:
        page = new_page(context)
        page.goto(LINKEDIN_LOGIN, wait_until="domcontentloaded", timeout=60_000)
        time.sleep(1.5)
        # Already warm profile → login redirects to feed
        if authed_url(page.url or ""):
            try:
                page.goto(
                    "https://www.linkedin.com/feed/",
                    wait_until="domcontentloaded",
                    timeout=30_000,
                )
                time.sleep(1.5)
            except Exception:  # noqa: BLE001
                pass
            final_url = page.url or ""
            logged_in = authed_url(final_url)
            return {
                "ok": logged_in,
                "status": "logged_in" if logged_in else "incomplete",
                "logged_in": logged_in,
                "challenge": "none",
                "final_url": final_url,
                "profile_dir": profile_dir,
                "hint": (
                    "Sessão LinkedIn já aquecida (perfil existente)."
                    if logged_in
                    else f"Redirect estranho após login: {final_url!r}"
                ),
                "source": "existing_profile",
            }
        t0 = time.time()
        _fill_credentials(page, sec)
        challenge = _await_post_password(page, timeout_sec=40)

        if challenge == "bad_creds":
            raise RuntimeError(
                "LinkedIn rejeitou email/senha — confira data/secrets/linkedin_account.yaml"
            )
        if challenge == "captcha":
            raise RuntimeError(
                "LinkedIn captcha/checkpoint — re-rode com WARM_BRIDGE_SESSION_HEADED=1"
            )
        if challenge == "sms":
            raise RuntimeError(
                "SMS 2FA fora de escopo — mude LinkedIn para email OTP ou autenticador "
                "(+ totp_secret no secrets yaml)."
            )

        if challenge == "email_otp":
            code = wait_for_linkedin_otp(sec, after_ts=t0, timeout_sec=otp_timeout)
            _fill_otp(page, code)
        elif challenge == "totp":
            if not sec.totp_secret:
                raise RuntimeError(
                    "Authenticator 2FA detectado — configure totp_secret no secrets yaml."
                )
            _fill_otp(page, generate_totp(sec.totp_secret))

        logged_in = _wait_feed(page, timeout_sec=90)
        if not logged_in:
            challenge = _await_post_password(page, timeout_sec=20)
            if challenge == "email_otp":
                code = wait_for_linkedin_otp(sec, after_ts=t0, timeout_sec=otp_timeout)
                _fill_otp(page, code)
                logged_in = _wait_feed(page, timeout_sec=60)
            elif challenge == "totp" and sec.totp_secret:
                _fill_otp(page, generate_totp(sec.totp_secret))
                logged_in = _wait_feed(page, timeout_sec=60)

        final_url = page.url or ""
        try:
            page.goto(
                "https://www.linkedin.com/feed/",
                wait_until="domcontentloaded",
                timeout=30_000,
            )
            time.sleep(2)
            final_url = page.url or final_url
            if authed_url(final_url):
                logged_in = True
        except Exception:  # noqa: BLE001
            pass

    status = "logged_in" if logged_in else "incomplete"
    hint = (
        "Sessão LinkedIn aquecida — Mapear no UI."
        if logged_in
        else f"Login incompleto (url={final_url!r}, challenge={challenge})."
    )
    return {
        "ok": logged_in,
        "status": status,
        "logged_in": logged_in,
        "challenge": challenge,
        "final_url": final_url,
        "profile_dir": profile_dir,
        "hint": hint,
    }
