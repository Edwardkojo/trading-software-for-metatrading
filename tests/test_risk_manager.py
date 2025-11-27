from datetime import datetime, timezone

from core.risk_manager import RiskLimits, RiskManager, TradeResult


def default_limits() -> RiskLimits:
    return RiskLimits(
        max_daily_loss=100,
        max_drawdown=500,
        max_consecutive_losses=3,
        max_open_trades=2,
        exposure_per_symbol=0.1,
        account_balance=10000,
        risk_per_trade=0.02,
    )


def test_risk_manager_position_size():
    manager = RiskManager(default_limits())
    size = manager.position_size(stop_loss_pips=20, pip_value=10)
    assert size > 0


def test_risk_manager_blocks_after_consecutive_losses():
    manager = RiskManager(default_limits())
    for _ in range(3):
        manager.register_trade_close(
            TradeResult(
                symbol="EURUSD",
                size=0.1,
                profit=-50,
                time=datetime.now(tz=timezone.utc),
            )
        )
    assert manager.consecutive_losses == 3
    assert not manager.can_open_trade("EURUSD", 0.1)


def test_risk_manager_daily_limit():
    manager = RiskManager(default_limits())
    manager.register_trade_close(
        TradeResult(
            symbol="EURUSD",
            size=0.1,
            profit=-150,
            time=datetime.now(tz=timezone.utc),
        )
    )
    assert manager.daily_limit_reached(datetime.now(tz=timezone.utc))

