"""
Trading engine orchestrating data, strategy, risk, and execution layers.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Protocol

from .data_handler import MarketDataProvider
from .persistence import TradeDatabase
from .position import TradePosition
from .risk_manager import RiskManager, TradeResult
from .trailing_stop import TrailingStopConfig, TrailingStopManager
from .utils import configure_logger, ensure_timezone, now_utc
from .metrics import MetricsTracker


class ExecutionProvider(Protocol):
    def send_order(self, symbol: str, size: float, side: str) -> str:
        ...

    def close_position(self, ticket: str) -> TradeResult:
        ...




class SimulatedExecutionProvider:
    """
    Mock execution layer for development and testing.
    """

    def __init__(self) -> None:
        self._ticket_counter = 0
        self.positions: Dict[str, TradePosition] = {}

    def send_order(self, symbol: str, size: float, side: str) -> str:
        self._ticket_counter += 1
        ticket = f"SIM-{self._ticket_counter}"
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
        profit = position.size * 10  # placeholder simulation
        return TradeResult(
            symbol=position.symbol,
            size=position.size,
            profit=profit,
            time=now_utc(),
        )


class MT5ExecutionProvider:
    """
    Execution provider that routes orders to MetaTrader5.
    """

    def __init__(
        self,
        login: int,
        password: str,
        server: str,
        deviation: int = 10,
    ) -> None:
        try:
            import MetaTrader5 as mt5  # type: ignore
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("MetaTrader5 package is required for MT5ExecutionProvider") from exc

        self.mt5 = mt5
        if not self.mt5.initialize(login=login, password=password, server=server):  # pragma: no cover
            raise RuntimeError(f"MetaTrader5 initialize failed: {self.mt5.last_error()}")
        self.deviation = deviation

    def send_order(self, symbol: str, size: float, side: str) -> str:  # pragma: no cover
        order_type = self.mt5.ORDER_TYPE_BUY if side == "buy" else self.mt5.ORDER_TYPE_SELL
        price = (
            self.mt5.symbol_info_tick(symbol).ask
            if side == "buy"
            else self.mt5.symbol_info_tick(symbol).bid
        )
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": size,
            "type": order_type,
            "price": price,
            "deviation": self.deviation,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        result = self.mt5.order_send(request)
        if result is None or result.retcode != self.mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 order_send failed: {self.mt5.last_error()}")
        return str(result.order)

    def close_position(self, ticket: str) -> TradeResult:  # pragma: no cover
        ticket_int = int(ticket)
        positions = self.mt5.positions_get(ticket=ticket_int)
        if not positions:
            raise RuntimeError(f"No MT5 position found for ticket {ticket}")
        position = positions[0]
        side = "buy" if position.type == self.mt5.ORDER_TYPE_BUY else "sell"
        close_type = self.mt5.ORDER_TYPE_SELL if side == "buy" else self.mt5.ORDER_TYPE_BUY
        price = (
            self.mt5.symbol_info_tick(position.symbol).bid
            if side == "buy"
            else self.mt5.symbol_info_tick(position.symbol).ask
        )
        request = {
            "action": self.mt5.TRADE_ACTION_DEAL,
            "position": ticket_int,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": close_type,
            "price": price,
            "deviation": self.deviation,
            "type_filling": self.mt5.ORDER_FILLING_IOC,
        }
        result = self.mt5.order_send(request)
        if result is None or result.retcode != self.mt5.TRADE_RETCODE_DONE:
            raise RuntimeError(f"MT5 close order failed: {self.mt5.last_error()}")

        profit = float(position.profit)
        return TradeResult(
            symbol=position.symbol,
            size=float(position.volume),
            profit=profit,
            time=now_utc(),
        )


class TradingEngine:
    def __init__(
        self,
        data_provider: MarketDataProvider,
        execution_provider: ExecutionProvider,
        strategy,
        risk_manager: RiskManager,
    ) -> None:
        self.data_provider = data_provider
        self.execution_provider = execution_provider
        self.strategy = strategy
        self.risk_manager = risk_manager
        self.positions: Dict[str, TradePosition] = {}
        self.logger = configure_logger("trading_engine")
        self.metrics = MetricsTracker()
        self.db = TradeDatabase()
        self.trailing_stop = TrailingStopManager(TrailingStopConfig())

    def process(self, symbol: str, prices: List[float], timestamp: datetime) -> None:
        signal = self.strategy.generate_signal(prices, symbol, timestamp)
        if not signal:
            return

        size = self.risk_manager.position_size(stop_loss_pips=20, pip_value=10)
        if not self.risk_manager.can_open_trade(symbol, size, timestamp):
            self.logger.info("Risk prevented trade for %s", symbol)
            return

        ticket = self.execution_provider.send_order(symbol, size, signal.side)
        position = TradePosition(
            ticket=ticket,
            symbol=symbol,
            size=size,
            entry_time=timestamp,
            side=signal.side,
        )
        self.positions[ticket] = position
        self.risk_manager.register_trade_open(symbol, size)
        
        # Register with trailing stop manager
        current_price = prices[-1] if prices else 0.0
        self.trailing_stop.register_position(ticket, position, current_price)
        
        self.logger.info("Opened %s trade for %s size %.2f", signal.side, symbol, size)

    def check_trailing_stops(self, symbol: str, current_price: float) -> None:
        """Check and trigger trailing stops for open positions."""
        tickets_to_close = []
        for ticket, position in self.positions.items():
            if position.symbol == symbol:
                if self.trailing_stop.update(ticket, position, current_price):
                    tickets_to_close.append(ticket)
        
        for ticket in tickets_to_close:
            self.logger.info("Trailing stop triggered for %s", ticket)
            self.close_position(ticket)

    def close_position(self, ticket: str) -> None:
        if ticket not in self.positions:
            return
        trade_result = self.execution_provider.close_position(ticket)
        self.risk_manager.register_trade_close(trade_result)
        self.metrics.add_trade(trade_result)
        self.db.save_trade(trade_result)
        self.trailing_stop.remove(ticket)
        del self.positions[ticket]

