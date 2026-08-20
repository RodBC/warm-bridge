"""Chrome driver attached to a local LinkedIn-logged profile (user-data-dir)."""

from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any

from .config import SessionConfig


@dataclass
class RateLimit:
    """Simple sleeps between LinkedIn navigations."""

    between_nav_s: float = 1.5
    after_action_s: float = 0.8


def _require_selenium() -> tuple[Any, Any]:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError(
            'Selenium não instalado. Rode: pip install -e ".[linkedin]"'
        ) from exc
    return webdriver, Options


def build_chrome(cfg: SessionConfig, *, headless: bool = False) -> Any:
    """Attach to an existing Chrome profile already logged into LinkedIn."""
    webdriver, Options = _require_selenium()
    options = Options()
    if cfg.user_data_dir:
        options.add_argument(f"--user-data-dir={cfg.user_data_dir}")
    if cfg.profile_directory:
        options.add_argument(f"--profile-directory={cfg.profile_directory}")
    if cfg.chrome_binary:
        options.binary_location = cfg.chrome_binary
    if headless or os.environ.get("WARM_BRIDGE_SELENIUM_HEADLESS") == "1":
        options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    if cfg.use_webdriver_manager:
        try:
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager

            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception:  # noqa: BLE001
            pass
    return webdriver.Chrome(options=options)


def polite_sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)


def quit_driver(driver: Any) -> None:
    try:
        driver.quit()
    except Exception:  # noqa: BLE001
        pass
