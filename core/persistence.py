"""
Persistence layer for storing trades, equity curves, and metrics.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .metrics import MetricsSnapshot
from .risk_manager import TradeResult
from .utils import ensure_timezone, now_utc


class TradeDatabase:
    """
    SQLite-based storage for trade history and equity snapshots.
    """

    def __init__(self, db_path: str = "logs/trades.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    size REAL NOT NULL,
                    profit REAL NOT NULL,
                    time TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS equity_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    equity REAL NOT NULL,
                    win_rate REAL NOT NULL,
                    profit_factor REAL NOT NULL,
                    sharpe_ratio REAL NOT NULL,
                    max_drawdown REAL NOT NULL
                )
            """
            )
            conn.commit()

    def save_trade(self, trade: TradeResult) -> None:
        """Store a completed trade."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO trades (symbol, size, profit, time, created_at) VALUES (?, ?, ?, ?, ?)",
                (
                    trade.symbol,
                    trade.size,
                    trade.profit,
                    trade.time.isoformat(),
                    now_utc().isoformat(),
                ),
            )
            conn.commit()

    def save_snapshot(self, snapshot: MetricsSnapshot) -> None:
        """Store a metrics snapshot."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO equity_snapshots 
                   (timestamp, equity, win_rate, profit_factor, sharpe_ratio, max_drawdown)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    now_utc().isoformat(),
                    snapshot.equity_curve[-1] if snapshot.equity_curve else 0.0,
                    snapshot.win_rate,
                    snapshot.profit_factor,
                    snapshot.sharpe_ratio,
                    snapshot.max_drawdown,
                ),
            )
            conn.commit()

    def get_recent_trades(self, limit: int = 100) -> List[TradeResult]:
        """Retrieve recent trades."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT symbol, size, profit, time FROM trades ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [
                TradeResult(
                    symbol=row["symbol"],
                    size=row["size"],
                    profit=row["profit"],
                    time=ensure_timezone(datetime.fromisoformat(row["time"])),
                )
                for row in rows
            ]

    def export_to_json(self, output_path: str) -> None:
        """Export all trades to JSON file."""
        trades = self.get_recent_trades(limit=10000)
        data = [
            {
                "symbol": t.symbol,
                "size": t.size,
                "profit": t.profit,
                "time": t.time.isoformat(),
            }
            for t in trades
        ]
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)


class SessionLogger:
    """
    Logs trading sessions with start/end times and summary metrics.
    """

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_start: Optional[datetime] = None

    def start_session(self) -> str:
        """Begin a new session and return session ID."""
        self.session_start = now_utc()
        session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"session_{session_id}.log"
        with open(log_file, "w") as f:
            f.write(f"Session started: {self.session_start.isoformat()}\n")
        return session_id

    def log_event(self, session_id: str, message: str) -> None:
        """Append an event to the session log."""
        log_file = self.log_dir / f"session_{session_id}.log"
        timestamp = now_utc().isoformat()
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")

    def end_session(
        self, session_id: str, positions_count: int, snapshot: MetricsSnapshot
    ) -> None:
        """Close session with summary."""
        log_file = self.log_dir / f"session_{session_id}.log"
        end_time = now_utc()
        duration = (end_time - self.session_start) if self.session_start else None
        with open(log_file, "a") as f:
            f.write(f"\nSession ended: {end_time.isoformat()}\n")
            if duration:
                f.write(f"Duration: {duration}\n")
            f.write(f"Open positions: {positions_count}\n")
            f.write(f"Win rate: {snapshot.win_rate:.2%}\n")
            f.write(f"Profit factor: {snapshot.profit_factor:.2f}\n")
            f.write(f"Max drawdown: {snapshot.max_drawdown:.2f}\n")
            f.write(f"Sharpe ratio: {snapshot.sharpe_ratio:.2f}\n")


