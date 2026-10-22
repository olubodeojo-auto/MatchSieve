"""Source-specific data collection adapters.

Each adapter owns page discovery, extraction rules, source metadata and gaps.
"""
from .soccerway import SoccerwayAdapter

__all__ = ["SoccerwayAdapter"]
