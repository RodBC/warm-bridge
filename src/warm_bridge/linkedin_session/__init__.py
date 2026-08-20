"""LinkedIn session intake via Camoufox — thin yellow-tier adapter.

Primary graph source per docs/sources.yaml remains Connections.csv + research.
Never invents edges. Mock: WARM_BRIDGE_SESSION_MOCK=1 (alias: WARM_BRIDGE_SELENIUM_MOCK).
"""

from .config import SessionConfig, load_session_config
from .service import SeleniumMapError, SessionMapError, map_target
from .session_status import friendly_map_error, session_status

__all__ = [
    "map_target",
    "SessionConfig",
    "load_session_config",
    "SessionMapError",
    "SeleniumMapError",
    "session_status",
    "friendly_map_error",
]
