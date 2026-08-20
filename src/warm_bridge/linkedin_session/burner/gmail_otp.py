"""Gmail OTP for LinkedIn email 2FA — IMAP app password first, OAuth optional."""

from __future__ import annotations

import base64
import email
import imaplib
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from ..otp_inbox.parse import extract_otp
from .secrets import AccountSecrets

GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
LINKEDIN_QUERY = (
    "from:(security-noreply@linkedin.com OR noreply@linkedin.com) newer_than:1d"
)
POLL_INTERVAL_S = 4.0
_IMAP_HOST = "imap.gmail.com"


def _imap_auth_error_message(exc: BaseException) -> str:
    low = str(exc).lower()
    if any(
        x in low
        for x in (
            "authenticationfailed",
            "invalid credentials",
            "login failed",
            "auth failed",
            "application-specific password",
        )
    ):
        return (
            "Gmail IMAP AUTH failed — need App Password (16 chars), "
            "not normal Gmail password. "
            "Google Account → Security → 2-Step Verification → App passwords."
        )
    return f"Gmail IMAP failed: {exc}"


def _imap_search_otp(secrets: AccountSecrets, *, after_ts: float) -> str | None:
    if not secrets.gmail_app_password:
        return None
    try:
        conn = imaplib.IMAP4_SSL(_IMAP_HOST)
        conn.login(secrets.email, secrets.gmail_app_password)
        conn.select("INBOX")
        typ, data = conn.search(None, '(FROM "linkedin.com")')
        if typ != "OK" or not data or not data[0]:
            conn.logout()
            return None
        for mid in reversed(data[0].split()[-15:]):
            typ, msg_data = conn.fetch(mid, "(RFC822)")
            if typ != "OK" or not msg_data or not msg_data[0]:
                continue
            raw = msg_data[0][1]
            if not isinstance(raw, (bytes, bytearray)):
                continue
            msg = email.message_from_bytes(raw)
            try:
                dt = parsedate_to_datetime(msg.get("Date", ""))
                if dt and dt.timestamp() < after_ts - 5:
                    continue
            except Exception:  # noqa: BLE001
                pass
            chunks: list[str] = [str(msg.get("Subject") or "")]
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() in ("text/plain", "text/html"):
                        try:
                            payload = part.get_payload(decode=True) or b""
                            chunks.append(payload.decode("utf-8", errors="replace"))
                        except Exception:  # noqa: BLE001
                            continue
            else:
                try:
                    payload = msg.get_payload(decode=True) or b""
                    chunks.append(payload.decode("utf-8", errors="replace"))
                except Exception:  # noqa: BLE001
                    pass
            code = extract_otp("\n".join(chunks))
            if code:
                conn.logout()
                return code
        conn.logout()
    except imaplib.IMAP4.error as exc:
        raise RuntimeError(_imap_auth_error_message(exc)) from exc
    except RuntimeError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(_imap_auth_error_message(exc)) from exc
    return None


def get_gmail_service(*, credentials_json: Path, token_json: Path) -> Any:
    """OAuth fallback — prefer gmail_app_password + IMAP."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError('Google API libs: pip install -e ".[linkedin]"') from exc

    creds = None
    if token_json.is_file():
        creds = Credentials.from_authorized_user_file(str(token_json), GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            from google_auth_oauthlib.flow import InstalledAppFlow

            if not credentials_json.is_file():
                raise FileNotFoundError(f"Gmail OAuth client ausente: {credentials_json}")
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_json), GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        token_json.parent.mkdir(parents=True, exist_ok=True)
        token_json.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds)


def _api_search_otp(secrets: AccountSecrets, *, after_ts: float) -> str | None:
    if not secrets.gmail_credentials_json or not secrets.gmail_token_json:
        return None
    service = get_gmail_service(
        credentials_json=secrets.gmail_credentials_json,
        token_json=secrets.gmail_token_json,
    )
    after_ms = int(after_ts * 1000)
    resp = service.users().messages().list(userId="me", q=LINKEDIN_QUERY, maxResults=10).execute()
    for item in resp.get("messages") or []:
        msg_id = item.get("id")
        if not msg_id:
            continue
        meta = service.users().messages().get(userId="me", id=msg_id, format="metadata").execute()
        if int(meta.get("internalDate") or 0) < after_ms - 2000:
            continue
        full = service.users().messages().get(userId="me", id=msg_id, format="full").execute()
        text = _message_body_text(full.get("payload") or {})
        code = extract_otp(text)
        if code:
            return code
    return None


def _message_body_text(payload: dict[str, Any]) -> str:
    parts: list[str] = []

    def walk(node: dict[str, Any]) -> None:
        body = node.get("body") or {}
        data = body.get("data")
        if data:
            try:
                parts.append(base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace"))
            except Exception:  # noqa: BLE001
                pass
        for child in node.get("parts") or []:
            if isinstance(child, dict):
                walk(child)

    walk(payload)
    headers = {
        h.get("name", "").lower(): h.get("value", "")
        for h in (payload.get("headers") or [])
        if isinstance(h, dict)
    }
    return (headers.get("subject") or "") + "\n" + "\n".join(parts)


def wait_for_linkedin_otp(
    secrets: AccountSecrets,
    *,
    after_ts: float,
    timeout_sec: float = 120,
) -> str:
    """Poll Gmail (IMAP app password preferred) for LinkedIn OTP."""
    if not secrets.gmail_app_password and not secrets.gmail_credentials_json:
        raise RuntimeError(
            "Precisa de gmail_app_password (16 chars) ou Gmail OAuth no secrets yaml."
        )
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        code = _imap_search_otp(secrets, after_ts=after_ts)
        if code:
            return code
        if secrets.gmail_credentials_json:
            try:
                code = _api_search_otp(secrets, after_ts=after_ts)
                if code:
                    return code
            except Exception:
                if not secrets.gmail_app_password:
                    raise
        time.sleep(POLL_INTERVAL_S)
    raise TimeoutError(
        f"Timeout aguardando OTP LinkedIn no Gmail ({timeout_sec:.0f}s) — "
        "email ainda não chegou ou filtro IMAP sem match. "
        "Confira gmail_app_password (App Password 16 chars, não senha normal)."
    )
