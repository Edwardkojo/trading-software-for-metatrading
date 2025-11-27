"""
Simple Moving Average (SMA) crossover strategy implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Sequence

from core.utils import ensure_timezone


def simple_moving_average(values: Sequence[float], period: int) -> List[float]:
    """
    Calculate SMA for the provided values.
    """
    if period <= 0:
        raise ValueError("SMA period must be positive")
    if len(values) < period:
        raise ValueError("Not enough data points to compute SMA")

    averages: List[float] = []
    window_sum = sum(values[:period])
    averages.append(window_sum / period)
    for idx in range(period, len(values)):
        window_sum += values[idx] - values[idx - period]
        averages.append(window_sum / period)
    return averages


@dataclass(frozen=True, slots=True)
class StrategySignal:
    symbol: str
    side: str
    time: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "time", ensure_timezone(self.time))


class SMACrossoverStrategy:
    """
    SMA crossover (fast vs slow) signal generator.
    """

    def __init__(self, fast_period: int = 10, slow_period: int = 30) -> None:
        if fast_period >= slow_period:
            raise ValueError("Fast SMA period must be less than slow period")
        self.fast_period = fast_period
        self.slow_period = slow_period

    def generate_signal(
        self,
        prices: Sequence[float],
        symbol: str,
        timestamp: datetime,
    ) -> StrategySignal | None:
        """
        Generate a buy or sell signal based on SMA crossover.
        """
        if len(prices) < self.slow_period + 1:
            return None

        fast_sma = simple_moving_average(prices, self.fast_period)
        slow_sma = simple_moving_average(prices, self.slow_period)

        fast_latest = fast_sma[-1]
        fast_prev = fast_sma[-2]
        slow_latest = slow_sma[-1]
        slow_prev = slow_sma[-2]

        if fast_prev <= slow_prev and fast_latest > slow_latest:
            return StrategySignal(symbol=symbol, side="buy", time=timestamp)
        if fast_prev >= slow_prev and fast_latest < slow_latest:
            return StrategySignal(symbol=symbol, side="sell", time=timestamp)
        return None

