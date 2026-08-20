"""Enter OTP / TOTP codes into LinkedIn challenge forms."""

from __future__ import annotations

import re
from typing import Any

from ..driver.rate_limit import polite_sleep

_OTP_INPUT_SELECTORS = [
    "input[name='pin']",
    "input#input__email_verification_pin",
    "input[aria-label*='verification']",
    "input[aria-label*='verificação']",
    "input[type='tel']",
    "input[inputmode='numeric']",
]

_SUBMIT_SELECTORS = [
    "button[type='submit']",
    "button[data-litms-control-urn*='submit']",
]


def submit_otp(page: Any, code: str, *, wait_after_s: float = 2.0) -> None:
    """Type a 6-digit code into the LinkedIn email-OTP / TOTP form."""
    digits = re.sub(r"\D", "", code or "")
    if len(digits) < 6:
        raise ValueError("OTP must contain at least 6 digits")

    filled = False
    for sel in _OTP_INPUT_SELECTORS:
        try:
            els = page.find_elements("css selector", sel)
        except Exception:  # noqa: BLE001
            els = []
        if not els:
            continue
        inp = els[0]
        raw_page = getattr(page, "_page", None)
        if raw_page is not None:
            loc = raw_page.locator(sel).first
            loc.fill(digits[:8])
            filled = True
            break
        try:
            inp.clear()
            inp.send_keys(digits[:8])
            filled = True
            break
        except Exception:  # noqa: BLE001
            continue

    if not filled:
        raise RuntimeError("Campo OTP não encontrado na página LinkedIn.")

    for sel in _SUBMIT_SELECTORS:
        try:
            btns = page.find_elements("css selector", sel)
        except Exception:  # noqa: BLE001
            btns = []
        if not btns:
            continue
        raw_page = getattr(page, "_page", None)
        if raw_page is not None:
            raw_page.locator(sel).first.click()
        else:
            btns[0].click()
        polite_sleep(wait_after_s)
        return

    raw_page = getattr(page, "_page", None)
    if raw_page is not None:
        raw_page.keyboard.press("Enter")
    polite_sleep(wait_after_s)
