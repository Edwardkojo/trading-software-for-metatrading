"""
Risk management logic enforcing trading guardrails.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List

from .utils import ensure_timezone, now_utc


@dataclass(slots=True)
class TradeResult:
    symbol: str
    size: float
    profit: float
    time: datetime

    def __post_init__(self) -> None:
        self.time = ensure_timezone(self.time)


@dataclass
class RiskLimits:
    max_daily_loss: float
    max_drawdown: float
    max_consecutive_losses: int
    max_open_trades: int
    exposure_per_symbol: float
    account_balance: float
    risk_per_trade: float


class RiskManager:
    """
    Evaluates whether new trades can be taken based on configured limits.
    """

    def __init__(self, limits: RiskLimits) -> None:
        self.limits = limits
        self.daily_loss: Dict[date, float] = {}
        self.consecutive_losses = 0
        self.equity_peak = limits.account_balance
        self.open_trades: Dict[str, float] = {}
        self.trade_history: List[TradeResult] = []

    def can_open_trade(self, symbol: str, size: float, current_time: datetime | None = None) -> bool:
        """
        Verify exposure, drawdown, consecutive losses, and open trade count.
        """
        check_time = ensure_timezone(current_time or now_utc())
        if self.daily_limit_reached(check_time):
            return False

        if len(self.open_trades) >= self.limits.max_open_trades:
            return False

        exposure = self.open_trades.get(symbol, 0.0) + size
        max_exposure = self.limits.account_balance * self.limits.exposure_per_symbol
        if exposure > max_exposure:
            return False

        if self.consecutive_losses >= self.limits.max_consecutive_losses:
            return False

        if self._current_drawdown() > self.limits.max_drawdown:
            return False

        return True

    def position_size(self, stop_loss_pips: float, pip_value: float) -> float:
        """
        Calculate position size using simple fixed-fraction formula.
        """
        if stop_loss_pips <= 0 or pip_value <= 0:
            raise ValueError("stop_loss_pips and pip_value must be positive")
        risk_amount = self.limits.account_balance * self.limits.risk_per_trade
        size = risk_amount / (stop_loss_pips * pip_value)
        return max(0.01, round(size, 2))

    def register_trade_open(self, symbol: str, size: float) -> None:
        self.open_trades[symbol] = self.open_trades.get(symbol, 0.0) + size

    def register_trade_close(self, trade: TradeResult) -> None:
        """
        Update loss streaks, exposure, equity, and drawdown state.
        """
        self.trade_history.append(trade)
        daily_key = trade.time.date()
        self.daily_loss[daily_key] = self.daily_loss.get(daily_key, 0.0) + trade.profit

        if trade.profit < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

        if trade.symbol in self.open_trades:
            self.open_trades[trade.symbol] = max(0.0, self.open_trades[trade.symbol] - trade.size)
            if self.open_trades[trade.symbol] == 0.0:
                del self.open_trades[trade.symbol]

        self.limits.account_balance += trade.profit
        self.equity_peak = max(self.equity_peak, self.limits.account_balance)

    def daily_limit_reached(self, current_time: datetime) -> bool:
        """
        Check if today's cumulative loss exceeds max daily loss.
        """
        now_date = ensure_timezone(current_time).date()
        losses = self.daily_loss.get(now_date, 0.0)
        return losses <= -abs(self.limits.max_daily_loss)

    def _current_drawdown(self) -> float:
        drawdown = self.equity_peak - self.limits.account_balance
        return max(0.0, drawdown)

