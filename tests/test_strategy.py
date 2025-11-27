from datetime import datetime, timezone

from strategies.sma_crossover import SMACrossoverStrategy, StrategySignal, simple_moving_average


def test_simple_moving_average_basic():
    data = [1, 2, 3, 4, 5]
    result = simple_moving_average(data, period=3)
    assert result == [2.0, 3.0, 4.0]


def test_sma_crossover_buy_signal():
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=4)
    prices = [5, 5, 5, 5, 1, 2, 3, 4]
    signal = strategy.generate_signal(prices, "EURUSD", datetime.now(tz=timezone.utc))
    assert isinstance(signal, StrategySignal)
    assert signal.side == "buy"


def test_sma_crossover_sell_signal():
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=4)
    prices = [1, 1, 1, 1, 5, 4, 3, 2]
    signal = strategy.generate_signal(prices, "EURUSD", datetime.now(tz=timezone.utc))
    assert isinstance(signal, StrategySignal)
    assert signal.side == "sell"


def test_sma_crossover_no_signal_with_insufficient_data():
    strategy = SMACrossoverStrategy(fast_period=2, slow_period=3)
    signal = strategy.generate_signal([1, 2], "EURUSD", datetime.now(tz=timezone.utc))
    assert signal is None

