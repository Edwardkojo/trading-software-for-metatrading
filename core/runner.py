"""
Continuous live-loop runner orchestrating warmup and execution cycles.
"""

from __future__ import annotations

import time
from datetime import timedelta
from typing import Dict, List

from .data_handler import MarketDataProvider
from .persistence import SessionLogger, TradeDatabase
from .trading_engine import TradingEngine
from .utils import configure_logger, ensure_timezone, now_utc


class LiveRunner:
    """
    Reusable loop controller for live or paper trading sessions.
    """

    def __init__(
        self,
        engine: TradingEngine,
        data_provider: MarketDataProvider,
        symbols: List[str],
        timeframe_minutes: int,
        warmup_bars: int,
        poll_interval_seconds: int,
    ) -> None:
        self.engine = engine
        self.data_provider = data_provider
        self.symbols = symbols
        self.timeframe = timedelta(minutes=max(1, timeframe_minutes))
        self.warmup_bars = max(10, warmup_bars)
        self.poll_interval = max(1, poll_interval_seconds)
        self.running = False
        self.prices: Dict[str, List[float]] = {symbol: [] for symbol in symbols}
        self.logger = configure_logger("live_runner")
        self.db = TradeDatabase()
        self.session_logger = SessionLogger()
        self.session_id: str | None = None

    def start(self) -> None:
        """
        Begin the warmup process followed by the continuous loop.
        """
        self.logger.info(
            "Starting LiveRunner for symbols=%s, timeframe=%s, poll=%ss",
            ",".join(self.symbols),
            self.timeframe,
            self.poll_interval,
        )
        self.running = True
        self.session_id = self.session_logger.start_session()
        self.logger.info("Session ID: %s", self.session_id)
        self._warmup()

        loop_count = 0
        try:
            while self.running:
                loop_count += 1
                for symbol in self.symbols:
                    self._process_symbol(symbol)

                if loop_count % 5 == 0:
                    self.logger.info("Heartbeat: %s loops processed", loop_count)
                    if self.session_id:
                        snapshot = self.engine.metrics.snapshot()
                        self.db.save_snapshot(snapshot)
                        self.session_logger.log_event(
                            self.session_id,
                            f"Heartbeat: {loop_count} loops, {len(self.engine.positions)} positions",
                        )

                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
            self.running = False
        finally:
            self._shutdown(loop_count)

    def _warmup(self) -> None:
        """
        Fetch initial historical data to seed price buffers.
        """
        for symbol in self.symbols:
            try:
                history = self.data_provider.fetch_historical(symbol, self.timeframe, self.warmup_bars)
                if not history:
                    self.logger.warning("No historical data for %s; skipping warmup", symbol)
                    continue
                closes = [bar.close for bar in history]
                self.prices[symbol] = closes[-self.warmup_bars :]
                self.logger.info("Warmup complete for %s (%s bars)", symbol, len(self.prices[symbol]))
            except Exception as exc:  # pragma: no cover - depends on live data
                self.logger.exception("Warmup failed for %s: %s", symbol, exc)

    def _process_symbol(self, symbol: str) -> None:
        """
        Fetch the latest tick and pass updated prices to the engine.
        """
        try:
            tick = self.data_provider.fetch_latest_tick(symbol)
        except Exception as exc:  # pragma: no cover - depends on live data
            self.logger.exception("Failed to fetch tick for %s: %s", symbol, exc)
            return

        price_list = self.prices.setdefault(symbol, [])
        price_list.append(tick.bid)
        if len(price_list) > self.warmup_bars:
            price_list.pop(0)

        try:
            # Check trailing stops first
            self.engine.check_trailing_stops(symbol, tick.bid)
            
            # Process new signals
            self.engine.process(symbol, price_list.copy(), ensure_timezone(tick.time))
        except Exception as exc:
            self.logger.exception("Processing error for %s: %s", symbol, exc)

    def _shutdown(self, loops: int) -> None:
        """
        Clean up resources and log session summary.
        """
        open_positions = len(self.engine.positions)
        equity = self.engine.risk_manager.limits.account_balance
        snapshot = self.engine.metrics.snapshot()
        
        # Save final snapshot and close session
        if self.session_id:
            self.db.save_snapshot(snapshot)
            self.session_logger.end_session(self.session_id, open_positions, snapshot)
        
        self.logger.info(
            "Runner stopping. Loops=%s OpenPositions=%s Equity=%.2f",
            loops,
            open_positions,
            equity,
        )

        if hasattr(self.data_provider, "mt5"):  # pragma: no cover - MT5 only
            try:
                self.data_provider.mt5.shutdown()
                self.logger.info("MT5 connection closed")
            except Exception as exc:
                self.logger.warning("MT5 shutdown issue: %s", exc)

