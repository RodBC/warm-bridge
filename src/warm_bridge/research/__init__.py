"""Public web research — cited insight on target/company (no LinkedIn login).

Never fabricates people or mutual edges. See docs/sources.yaml public_web_research.
"""

from .service import ResearchError, research_target

__all__ = ["research_target", "ResearchError"]
