"""
Performance analytics for the trading system.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

from .risk_manager import TradeResult


@dataclass
class MetricsSnapshot:
    equity_curve: List[float] = field(default_factory=list)
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0


class MetricsTracker:
    def __init__(self) -> None:
        self.trades: List[TradeResult] = []
        self.equity_curve: List[float] = []

    def add_trade(self, trade: TradeResult) -> None:
        self.trades.append(trade)
        balance = (self.equity_curve[-1] if self.equity_curve else 0.0) + trade.profit
        self.equity_curve.append(balance)

    def snapshot(self) -> MetricsSnapshot:
        return MetricsSnapshot(
            equity_curve=self.equity_curve.copy(),
            win_rate=self._win_rate(),
            profit_factor=self._profit_factor(),
            sharpe_ratio=self._sharpe_ratio(),
            max_drawdown=self._max_drawdown(),
        )

    def _win_rate(self) -> float:
        if not self.trades:
            return 0.0
        wins = sum(1 for trade in self.trades if trade.profit > 0)
        return wins / len(self.trades)

    def _profit_factor(self) -> float:
        gross_profit = sum(trade.profit for trade in self.trades if trade.profit > 0)
        gross_loss = sum(-trade.profit for trade in self.trades if trade.profit < 0)
        if gross_loss == 0:
            return float("inf") if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    def _sharpe_ratio(self) -> float:
        if len(self.trades) < 2:
            return 0.0
        returns = [trade.profit for trade in self.trades]
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
        std_dev = math.sqrt(variance)
        if std_dev == 0:
            return 0.0
        return avg_return / std_dev

    def _max_drawdown(self) -> float:
        peak = 0.0
        max_dd = 0.0
        for equity in self.equity_curve:
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
        return max_dd

