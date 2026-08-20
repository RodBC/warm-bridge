"""Backward-compat re-exports — prefer warm_bridge.linkedin_session."""

from ..linkedin_session import (
    SeleniumMapError,
    SessionConfig,
    friendly_map_error,
    load_session_config,
    map_target,
    session_status,
)

__all__ = [
    "map_target",
    "SessionConfig",
    "load_session_config",
    "SeleniumMapError",
    "session_status",
    "friendly_map_error",
]
