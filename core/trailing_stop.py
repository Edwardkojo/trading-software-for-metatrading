"""
Trailing stop loss management for open positions.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .position import TradePosition
from .utils import configure_logger


@dataclass
class TrailingStopConfig:
    """Configuration for trailing stop behavior."""

    enabled: bool = True
    initial_pips: float = 20.0
    trailing_pips: float = 10.0
    step_pips: float = 5.0


class TrailingStopManager:
    """
    Manages trailing stop losses for open positions.
    """

    def __init__(self, config: TrailingStopConfig) -> None:
        self.config = config
        self.stop_levels: Dict[str, float] = {}  # ticket -> stop price
        self.highest_prices: Dict[str, float] = {}  # ticket -> highest price seen
        self.logger = configure_logger("trailing_stop")

    def register_position(self, ticket: str, position: TradePosition, current_price: float) -> None:
        """Register a new position and set initial stop."""
        if not self.config.enabled:
            return

        if position.side == "buy":
            initial_stop = current_price - (self.config.initial_pips * 0.0001)
            self.stop_levels[ticket] = initial_stop
            self.highest_prices[ticket] = current_price
        else:  # sell
            initial_stop = current_price + (self.config.initial_pips * 0.0001)
            self.stop_levels[ticket] = initial_stop
            self.highest_prices[ticket] = current_price

        self.logger.info(
            "Trailing stop set for %s: initial=%.5f, current=%.5f",
            ticket,
            initial_stop,
            current_price,
        )

    def update(self, ticket: str, position: TradePosition, current_price: float) -> bool:
        """
        Update trailing stop and return True if stop should be triggered.
        """
        if not self.config.enabled or ticket not in self.stop_levels:
            return False

        current_stop = self.stop_levels[ticket]
        highest = self.highest_prices[ticket]

        if position.side == "buy":
            if current_price > highest:
                self.highest_prices[ticket] = current_price
                new_stop = current_price - (self.config.trailing_pips * 0.0001)
                if new_stop > current_stop + (self.config.step_pips * 0.0001):
                    self.stop_levels[ticket] = new_stop
                    self.logger.info("Trailing stop updated for %s: %.5f -> %.5f", ticket, current_stop, new_stop)

            if current_price <= self.stop_levels[ticket]:
                return True
        else:  # sell
            if current_price < highest:
                self.highest_prices[ticket] = current_price
                new_stop = current_price + (self.config.trailing_pips * 0.0001)
                if new_stop < current_stop - (self.config.step_pips * 0.0001):
                    self.stop_levels[ticket] = new_stop
                    self.logger.info("Trailing stop updated for %s: %.5f -> %.5f", ticket, current_stop, new_stop)

            if current_price >= self.stop_levels[ticket]:
                return True

        return False

    def remove(self, ticket: str) -> None:
        """Remove trailing stop tracking for a closed position."""
        self.stop_levels.pop(ticket, None)
        self.highest_prices.pop(ticket, None)

