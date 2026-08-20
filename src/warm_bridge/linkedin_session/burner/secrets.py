"""Load gitignored LinkedIn account credentials — auto-login on serve/map."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ...models import ROOT

ACCOUNT_YAML = ROOT / "data" / "secrets" / "linkedin_account.yaml"
LEGACY_BURNER_YAML = ROOT / "data" / "secrets" / "linkedin_burner.yaml"


@dataclass
class AccountSecrets:
    email: str
    password: str
    linkedin_url: str = ""
    totp_secret: str = ""
    # Prefer IMAP app password (least friction). OAuth JSON optional fallback.
    gmail_app_password: str = ""
    gmail_credentials_json: Path | None = None
    gmail_token_json: Path | None = None
    profile_dir: str = ""


BurnerSecrets = AccountSecrets


def looks_like_gmail_app_password(raw: str) -> bool:
    """Google App Passwords are 16 alphanumeric chars (optional spaces)."""
    cleaned = (raw or "").replace(" ", "").strip()
    if len(cleaned) != 16:
        return False
    return cleaned.isalnum()


def validate_secrets_for_bootstrap(sec: AccountSecrets) -> None:
    """Preflight before burner login — reject normal Gmail password as IMAP secret."""
    if not sec.email or not sec.password:
        raise ValueError("Secrets yaml precisa de email e password (ops only).")
    if sec.totp_secret and not sec.gmail_app_password and not sec.gmail_credentials_json:
        return
    if sec.gmail_app_password and not looks_like_gmail_app_password(sec.gmail_app_password):
        raise ValueError(
            "Need Gmail App Password (16 chars), not login password. "
            "Google Account → Security → 2-Step Verification → App passwords."
        )
    if not sec.gmail_app_password and not sec.gmail_credentials_json and not sec.totp_secret:
        raise ValueError(
            "Configure gmail_app_password (16-char App Password) ou totp_secret "
            "para 2FA. Senha normal do Gmail não funciona no IMAP."
        )


def account_secrets_path() -> Path | None:
    if ACCOUNT_YAML.is_file():
        return ACCOUNT_YAML
    if LEGACY_BURNER_YAML.is_file():
        return LEGACY_BURNER_YAML
    return None


def burner_secrets_path() -> Path:
    p = account_secrets_path()
    return p or ACCOUNT_YAML


def account_secrets_present() -> bool:
    path = account_secrets_path()
    if not path:
        return False
    try:
        sec = load_account_secrets(path)
        return bool(sec.email and sec.password)
    except Exception:  # noqa: BLE001
        return False


def burner_secrets_present() -> bool:
    return account_secrets_present()


def load_account_secrets(path: Path | None = None) -> AccountSecrets:
    cfg_path = path or account_secrets_path()
    if not cfg_path or not cfg_path.is_file():
        raise FileNotFoundError(
            f"Conta LinkedIn ausente. Crie: {ACCOUNT_YAML}\n"
            "Paste credentials in chat — agent writes this file."
        )
    import yaml

    data: dict[str, Any] = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML inválido: {cfg_path}")

    def _path(key: str) -> Path | None:
        raw = str(data.get(key) or "").strip()
        if not raw:
            return None
        p = Path(raw)
        if not p.is_absolute():
            p = ROOT / p
        return p

    profile = str(data.get("profile_dir") or "").strip()
    if profile and not Path(profile).is_absolute():
        profile = str(ROOT / profile)

    return AccountSecrets(
        email=str(data.get("email") or "").strip(),
        password=str(data.get("password") or ""),
        linkedin_url=str(data.get("linkedin_url") or data.get("seller_linkedin") or "").strip(),
        totp_secret=str(data.get("totp_secret") or "").strip(),
        gmail_app_password=str(
            data.get("gmail_app_password") or data.get("app_password") or ""
        ).replace(" ", ""),
        gmail_credentials_json=_path("gmail_credentials_json"),
        gmail_token_json=_path("gmail_token_json"),
        profile_dir=profile,
    )


def load_burner_secrets(path: Path | None = None) -> AccountSecrets:
    return load_account_secrets(path)


def write_account_secrets(
    *,
    email: str,
    password: str,
    gmail_app_password: str = "",
    linkedin_url: str = "",
    totp_secret: str = "",
    path: Path | None = None,
) -> Path:
    """Write gitignored secrets. Never commit."""
    import yaml

    app_pw = gmail_app_password.replace(" ", "").strip()
    if app_pw and not looks_like_gmail_app_password(app_pw):
        raise ValueError(
            "Need Gmail App Password (16 chars), not login password. "
            "Google Account → Security → 2-Step Verification → App passwords."
        )

    cfg_path = path or ACCOUNT_YAML
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "email": email.strip(),
        "password": password,
        "gmail_app_password": app_pw,
        "profile_dir": "data/camoufox_profile",
    }
    if linkedin_url.strip():
        payload["linkedin_url"] = linkedin_url.strip()
    if totp_secret.strip():
        payload["totp_secret"] = totp_secret.strip()
    cfg_path.write_text(
        yaml.safe_dump(payload, default_flow_style=False, allow_unicode=True),
        encoding="utf-8",
    )
    try:
        cfg_path.chmod(0o600)
    except OSError:
        pass
    return cfg_path
