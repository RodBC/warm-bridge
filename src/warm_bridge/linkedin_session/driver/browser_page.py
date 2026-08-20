"""BrowserPage protocol — shared by Camoufox (Playwright) and legacy Selenium adapters."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BrowserPage(Protocol):
    """Minimal surface used by mutuals/enrich scrapers."""

    def get(self, url: str) -> None: ...

    def find_elements(self, by: str, selector: str) -> list[Any]: ...

    def find_element(self, by: str, selector: str) -> Any: ...


class PlaywrightElementAdapter:
    def __init__(self, locator: Any) -> None:
        self._loc = locator

    def find_element(self, by: str, selector: str) -> PlaywrightElementAdapter:
        if by != "css selector":
            raise ValueError(f"unsupported selector type: {by}")
        return PlaywrightElementAdapter(self._loc.locator(selector).first)

    def find_elements(self, by: str, selector: str) -> list[PlaywrightElementAdapter]:
        if by != "css selector":
            raise ValueError(f"unsupported selector type: {by}")
        loc = self._loc.locator(selector)
        count = loc.count()
        return [PlaywrightElementAdapter(loc.nth(i)) for i in range(count)]

    def get_attribute(self, name: str) -> str | None:
        try:
            if name == "href":
                return self._loc.get_attribute("href")
            if name == "src":
                return self._loc.get_attribute("src")
            if name == "data-delayed-url":
                return self._loc.get_attribute("data-delayed-url")
            return self._loc.get_attribute(name)
        except Exception:  # noqa: BLE001
            return None

    @property
    def text(self) -> str:
        try:
            return (self._loc.inner_text() or "").strip()
        except Exception:  # noqa: BLE001
            return ""


class PlaywrightBrowserPage:
    """Wrap Playwright Page with Selenium-shaped helpers."""

    def __init__(self, page: Any) -> None:
        self._page = page

    def get(self, url: str) -> None:
        self._page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    def find_elements(self, by: str, selector: str) -> list[PlaywrightElementAdapter]:
        if by != "css selector":
            raise ValueError(f"unsupported selector type: {by}")
        loc = self._page.locator(selector)
        count = loc.count()
        return [PlaywrightElementAdapter(loc.nth(i)) for i in range(count)]

    def find_element(self, by: str, selector: str) -> PlaywrightElementAdapter:
        if by != "css selector":
            raise ValueError(f"unsupported selector type: {by}")
        return PlaywrightElementAdapter(self._page.locator(selector).first)


class SeleniumBrowserPage:
    """Wrap Selenium WebDriver as BrowserPage (legacy backend)."""

    def __init__(self, driver: Any) -> None:
        self._driver = driver

    def get(self, url: str) -> None:
        self._driver.get(url)

    def find_elements(self, by: str, selector: str) -> list[Any]:
        return self._driver.find_elements(by, selector)

    def find_element(self, by: str, selector: str) -> Any:
        return self._driver.find_element(by, selector)
