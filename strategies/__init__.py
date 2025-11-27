"""
Strategies package exposing available trading strategies.
"""

from .sma_crossover import SMACrossoverStrategy, StrategySignal, simple_moving_average

__all__ = [
    "SMACrossoverStrategy",
    "StrategySignal",
    "simple_moving_average",
]

