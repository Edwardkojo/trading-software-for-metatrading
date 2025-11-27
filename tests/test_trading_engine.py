from datetime import datetime, timezone

from core.risk_manager import RiskLimits, RiskManager
from core.trading_engine import SimulatedExecutionProvider, TradingEngine
from strategies.sma_crossover import StrategySignal


class DummyStrategy:
    def generate_signal(self, prices, symbol, timestamp):
        return StrategySignal(symbol=symbol, side="buy", time=timestamp)


class DummyDataProvider:
    def fetch_latest_tick(self, symbol):
        raise NotImplementedError

    def fetch_historical(self, symbol, timeframe, bars):
        raise NotImplementedError


def default_limits() -> RiskLimits:
    return RiskLimits(
        max_daily_loss=1000,
        max_drawdown=5000,
        max_consecutive_losses=10,
        max_open_trades=5,
        exposure_per_symbol=1.0,
        account_balance=10000,
        risk_per_trade=0.01,
    )


def test_trading_engine_opens_and_closes_trades():
    engine = TradingEngine(
        data_provider=DummyDataProvider(),
        execution_provider=SimulatedExecutionProvider(),
        strategy=DummyStrategy(),
        risk_manager=RiskManager(default_limits()),
    )

    timestamp = datetime.now(tz=timezone.utc)
    engine.process("EURUSD", [1, 1.1, 1.2], timestamp)
    assert engine.positions

    ticket = next(iter(engine.positions))
    engine.close_position(ticket)
    assert not engine.positions
    assert engine.metrics.equity_curve

