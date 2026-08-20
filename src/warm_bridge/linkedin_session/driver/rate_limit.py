"""Simple sleeps between LinkedIn navigations."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class RateLimit:
    between_nav_s: float = 1.5
    after_action_s: float = 0.8


def polite_sleep(seconds: float) -> None:
    if seconds > 0:
        time.sleep(seconds)
