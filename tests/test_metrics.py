from datetime import datetime, timezone

from core.metrics import MetricsTracker
from core.risk_manager import TradeResult


def make_trade(profit: float) -> TradeResult:
    return TradeResult(
        symbol="EURUSD",
        size=0.1,
        profit=profit,
        time=datetime.now(tz=timezone.utc),
    )


def test_metrics_snapshot():
    metrics = MetricsTracker()
    metrics.add_trade(make_trade(50))
    metrics.add_trade(make_trade(-20))

    snapshot = metrics.snapshot()
    assert snapshot.win_rate == 0.5
    assert snapshot.equity_curve[-1] == 30
    assert snapshot.max_drawdown >= 0

