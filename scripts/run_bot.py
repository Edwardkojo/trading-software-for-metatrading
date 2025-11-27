"""
Entrypoint for running the trading bot with either MT5 or simulated execution.
"""

from config import load_config
from core.data_handler import MT5DataProvider, SimulatedDataProvider
from core.runner import LiveRunner
from core.risk_manager import RiskLimits, RiskManager
from core.trading_engine import MT5ExecutionProvider, SimulatedExecutionProvider, TradingEngine
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
    config = load_config()
    print(f"Starting tradin-AI bot in {config.run_mode} mode...")

    if config.use_mt5 and config.mt5.login and config.mt5.password and config.mt5.server:
        data_provider = MT5DataProvider()
        execution_provider = MT5ExecutionProvider(
            login=config.mt5.login,
            password=config.mt5.password,
            server=config.mt5.server,
            deviation=config.mt5.deviation,
        )
    else:
        data_provider = SimulatedDataProvider()
        execution_provider = SimulatedExecutionProvider()

    engine = TradingEngine(
        data_provider=data_provider,
        execution_provider=execution_provider,
        strategy=SMACrossoverStrategy(),
        risk_manager=RiskManager(default_limits()),
    )

    runner = LiveRunner(
        engine=engine,
        data_provider=data_provider,
        symbols=config.symbols,
        timeframe_minutes=config.timeframe_minutes,
        warmup_bars=config.warmup_bars,
        poll_interval_seconds=config.poll_interval_seconds,
    )

    runner.start()
    print("tradin-AI bot stopped cleanly.")


if __name__ == "__main__":
    main()

