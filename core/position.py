"""
Position data structures for trading engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .utils import ensure_timezone


@dataclass
class TradePosition:
    ticket: str
    symbol: str
    size: float
    entry_time: datetime
    side: str

    def __post_init__(self) -> None:
        self.entry_time = ensure_timezone(self.entry_time)

