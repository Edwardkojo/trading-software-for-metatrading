from datetime import timedelta

from core.backtesting import Backtester
from core.data_handler import SimulatedDataProvider
from core.risk_manager import RiskLimits, RiskManager
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


def test_backtester_generates_metrics():
    data_provider = SimulatedDataProvider()
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=3)
    risk_manager = RiskManager(default_limits())

    backtester = Backtester(
        data_provider=data_provider,
        strategy=strategy,
        risk_manager=risk_manager,
    )

    result = backtester.run("EURUSD", timedelta(minutes=1), 20)
    assert result.metrics.max_drawdown >= 0
    assert result.metrics.win_rate >= 0

