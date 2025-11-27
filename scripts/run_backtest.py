"""
Helper script to execute a quick backtest using the simulated provider.
"""

from datetime import timedelta

from core.backtesting import Backtester
from core.data_handler import SimulatedDataProvider
from core.risk_manager import RiskLimits, RiskManager
from strategies import SMACrossoverStrategy


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


def main() -> None:
    backtester = Backtester(
        data_provider=SimulatedDataProvider(),
        strategy=SMACrossoverStrategy(),
        risk_manager=RiskManager(default_limits()),
    )
    result = backtester.run("EURUSD", timedelta(minutes=1), 200)
    snapshot = result.metrics
    print("Trades:", len(result.trades))
    print("Win rate:", snapshot.win_rate)
    print("Profit factor:", snapshot.profit_factor)
    print("Max drawdown:", snapshot.max_drawdown)


if __name__ == "__main__":
    main()

