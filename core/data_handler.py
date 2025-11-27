"""
Data handling utilities for both live and simulated trading.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Protocol

from .utils import ensure_timezone, now_utc


class MarketDataProvider(Protocol):
    """Protocol describing required market data operations."""

    def fetch_latest_tick(self, symbol: str) -> "Tick":
        ...

    def fetch_historical(
        self,
        symbol: str,
        timeframe: timedelta,
        bars: int,
    ) -> List["Bar"]:
        ...


@dataclass(slots=True)
class Tick:
    symbol: str
    bid: float
    ask: float
    time: datetime

    def __post_init__(self) -> None:
        self.time = ensure_timezone(self.time)


@dataclass(slots=True)
class Bar:
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    time: datetime

    def __post_init__(self) -> None:
        self.time = ensure_timezone(self.time)


class SimulatedDataProvider(MarketDataProvider):
    """
    Deterministic pseudo-random provider for tests and offline development.
    """

    def __init__(self, seed: int = 42) -> None:
        self.random = random.Random(seed)

    def fetch_latest_tick(self, symbol: str) -> Tick:
        price = 1.0 + self.random.random() * 0.01
        spread = 0.0002
        now = now_utc()
        return Tick(
            symbol=symbol,
            bid=round(price, 5),
            ask=round(price + spread, 5),
            time=now,
        )

    def fetch_historical(
        self,
        symbol: str,
        timeframe: timedelta,
        bars: int,
    ) -> List[Bar]:
        now = now_utc()
        prices = [1.0]
        for _ in range(bars):
            delta = (self.random.random() - 0.5) * 0.01
            prices.append(max(0.5, prices[-1] + delta))

        candles: List[Bar] = []
        for idx in range(1, len(prices)):
            time = now - timeframe * (len(prices) - idx)
            base = prices[idx]
            high = base + self.random.random() * 0.002
            low = base - self.random.random() * 0.002
            candles.append(
                Bar(
                    symbol=symbol,
                    open=base,
                    high=max(high, base),
                    low=min(low, base),
                    close=base,
                    volume=1000 + self.random.random() * 100,
                    time=time,
                )
            )
        return candles


class MT5DataProvider(MarketDataProvider):
    """
    Lightweight wrapper around MetaTrader5 for live usage.
    """

    def __init__(self) -> None:
        try:
            import MetaTrader5 as mt5  # type: ignore

            self.mt5 = mt5
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("MetaTrader5 package is required for MT5DataProvider") from exc

        if not self.mt5.initialize():  # pragma: no cover
            raise RuntimeError(f"MetaTrader5 initialize failed: {self.mt5.last_error()}")

    def fetch_latest_tick(self, symbol: str) -> Tick:  # pragma: no cover - requires MT5
        tick = self.mt5.symbol_info_tick(symbol)
        if tick is None:
            raise RuntimeError(f"Unable to fetch tick for {symbol}")

        return Tick(
            symbol=symbol,
            bid=float(tick.bid),
            ask=float(tick.ask),
            time=datetime.fromtimestamp(tick.time_msc / 1000, tz=timezone.utc),
        )

    def fetch_historical(
        self,
        symbol: str,
        timeframe: timedelta,
        bars: int,
    ) -> List[Bar]:  # pragma: no cover - requires MT5
        mt5_tf = self._map_timeframe(timeframe)
        rates = self.mt5.copy_rates_from_pos(symbol, mt5_tf, 0, bars)
        if rates is None:
            raise RuntimeError(f"Unable to fetch rates for {symbol}")

        return [
            Bar(
                symbol=symbol,
                open=float(rate.open),
                high=float(rate.high),
                low=float(rate.low),
                close=float(rate.close),
                volume=float(rate.tick_volume),
                time=datetime.fromtimestamp(rate.time, tz=timezone.utc),
            )
            for rate in rates
        ]

    def _map_timeframe(self, timeframe: timedelta) -> int:
        minutes = int(timeframe.total_seconds() // 60)
        mapping = {
            1: self.mt5.TIMEFRAME_M1,
            5: self.mt5.TIMEFRAME_M5,
            15: self.mt5.TIMEFRAME_M15,
            60: self.mt5.TIMEFRAME_H1,
            240: self.mt5.TIMEFRAME_H4,
            1440: self.mt5.TIMEFRAME_D1,
        }
        if minutes not in mapping:
            raise ValueError(f"Unsupported timeframe: {timeframe}")
        return mapping[minutes]

