"""TOTP for burner accounts using authenticator-app 2FA."""

from __future__ import annotations


def generate_totp(secret: str) -> str:
    try:
        import pyotp
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError('pyotp não instalado. Rode: pip install -e ".[linkedin]"') from exc
    clean = (secret or "").replace(" ", "").upper()
    if not clean:
        raise ValueError("totp_secret vazio no burner yaml")
    return pyotp.TOTP(clean).now()
