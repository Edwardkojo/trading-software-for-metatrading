"""
Application configuration helpers.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG_PATH = Path("config/default.json")


@dataclass
class MT5Settings:
    login: int | None = None
    password: str | None = None
    server: str | None = None
    deviation: int = 10


@dataclass
class AppConfig:
    use_mt5: bool = False
    mt5: MT5Settings = field(default_factory=MT5Settings)
    symbols: list[str] = field(default_factory=lambda: ["EURUSD"])
    timeframe_minutes: int = 5
    poll_interval_seconds: int = 5
    warmup_bars: int = 200
    run_mode: str = "paper"


def _load_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_config(path: Path | None = None) -> AppConfig:
    """
    Load application configuration from JSON and environment overrides.
    """
    target = path or DEFAULT_CONFIG_PATH
    data = _load_file(target)

    env_use_mt5 = os.getenv("TRADIN_USE_MT5")
    if env_use_mt5 is not None:
        data["use_mt5"] = env_use_mt5.lower() in {"1", "true", "yes"}

    mt5_data = data.get("mt5", {})
    env_login = os.getenv("TRADIN_MT5_LOGIN")
    env_password = os.getenv("TRADIN_MT5_PASSWORD")
    env_server = os.getenv("TRADIN_MT5_SERVER")
    env_deviation = os.getenv("TRADIN_MT5_DEVIATION")

    if env_login is not None:
        mt5_data["login"] = int(env_login)
    if env_password is not None:
        mt5_data["password"] = env_password
    if env_server is not None:
        mt5_data["server"] = env_server
    if env_deviation is not None:
        mt5_data["deviation"] = int(env_deviation)

    # Convert login to int if it's a string or number
    login_value = mt5_data.get("login")
    if login_value is not None:
        try:
            login_value = int(login_value)
        except (ValueError, TypeError):
            login_value = None
    
    return AppConfig(
        use_mt5=data.get("use_mt5", False),
        mt5=MT5Settings(
            login=login_value,
            password=mt5_data.get("password"),
            server=mt5_data.get("server"),
            deviation=mt5_data.get("deviation", 10),
        ),
        symbols=data.get("symbols", ["EURUSD"]),
        timeframe_minutes=data.get("timeframe_minutes", 5),
        poll_interval_seconds=data.get("poll_interval_seconds", 5),
        warmup_bars=data.get("warmup_bars", 200),
        run_mode=data.get("run_mode", "paper"),
    )

