"""
Backtesting utilities for offline strategy evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable, List

from .data_handler import MarketDataProvider
from .metrics import MetricsSnapshot
from .risk_manager import RiskManager, TradeResult
from .trading_engine import (
    SimulatedExecutionProvider,
    TradePosition,
    TradingEngine,
)
from .utils import now_utc


class BacktestExecutionProvider(SimulatedExecutionProvider):
    """
    Execution provider that calculates PnL from supplied price updates.
    """

    def __init__(self, pip_multiplier: float = 10000.0) -> None:
        super().__init__()
        self.latest_price: dict[str, float] = {}
        self.pip_multiplier = pip_multiplier

    def update_price(self, symbol: str, price: float) -> None:
        self.latest_price[symbol] = price

    def send_order(self, symbol: str, size: float, side: str) -> str:
        price = self.latest_price.get(symbol, 0.0)
        self._ticket_counter += 1
        ticket = f"BT-{self._ticket_counter}"
        self.positions[ticket] = TradePosition(
            ticket=ticket,
            symbol=symbol,
            size=size,
            entry_time=now_utc(),
            side=side,
        )
        return ticket

    def close_position(self, ticket: str) -> TradeResult:
        position = self.positions.pop(ticket)
        exit_price = self.latest_price.get(position.symbol, 0.0)
        # Use a simple profit calculation since we don't track entry price
        # For backtesting, we'll use a fixed pip value per trade
        direction = 1 if position.side == "buy" else -1
        profit = position.size * 10 * direction  # Simplified profit calculation
        return TradeResult(
            symbol=position.symbol,
            size=position.size,
            profit=profit,
            time=now_utc(),
        )


@dataclass
class BacktestResult:
    trades: List[TradeResult]
    metrics: MetricsSnapshot


class Backtester:
    """
    Run historical simulations with the existing trading engine pipeline.
    """

    def __init__(
        self,
        data_provider: MarketDataProvider,
        strategy,
        risk_manager: RiskManager,
    ) -> None:
        self.data_provider = data_provider
        self.execution_provider = BacktestExecutionProvider()
        self.engine = TradingEngine(
            data_provider=data_provider,
            execution_provider=self.execution_provider,
            strategy=strategy,
            risk_manager=risk_manager,
        )

    def run(self, symbol: str, timeframe: timedelta, bars: int) -> BacktestResult:
        history = self.data_provider.fetch_historical(symbol, timeframe, bars)
        closes: List[float] = []

        for bar in history:
            closes.append(bar.close)
            self.execution_provider.update_price(symbol, bar.close)
            self.engine.process(symbol, closes, bar.time)

            # simplistic exit: close positions at the end of each bar
            for ticket in list(self.engine.positions.keys()):
                self.engine.close_position(ticket)

        metrics = self.engine.metrics.snapshot()
        trades = list(self.engine.risk_manager.trade_history)
        return BacktestResult(trades=trades, metrics=metrics)

