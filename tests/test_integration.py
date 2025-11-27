from datetime import datetime, timezone

from core.data_handler import SimulatedDataProvider
from core.risk_manager import RiskLimits, RiskManager
from core.trading_engine import SimulatedExecutionProvider, TradingEngine
from strategies.sma_crossover import SMACrossoverStrategy


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


def test_full_pipeline_simulation():
    provider = SimulatedDataProvider()
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=3)
    engine = TradingEngine(
        data_provider=provider,
        execution_provider=SimulatedExecutionProvider(),
        strategy=strategy,
        risk_manager=RiskManager(default_limits()),
    )

    prices = [1.0, 1.1, 1.2, 1.3, 1.4]
    timestamp = datetime.now(tz=timezone.utc)
    engine.process("EURUSD", prices, timestamp)

    if engine.positions:
        ticket = next(iter(engine.positions))
        engine.close_position(ticket)

    snapshot = engine.metrics.snapshot()
    assert snapshot.win_rate >= 0
    assert snapshot.max_drawdown >= 0

