from pathlib import Path

from config.settings import load_config


def test_load_config_from_file(tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text(
        """
        {
            "use_mt5": true,
            "mt5": {
                "login": 123,
                "password": "secret",
                "server": "Broker-Server",
                "deviation": 15
            }
        }
        """,
        encoding="utf-8",
    )

    config = load_config(cfg_path)
    assert config.use_mt5 is True
    assert config.mt5.login == 123
    assert config.mt5.deviation == 15


def test_environment_overrides(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.json"
    cfg_path.write_text("{}", encoding="utf-8")

    monkeypatch.setenv("TRADIN_USE_MT5", "true")
    monkeypatch.setenv("TRADIN_MT5_LOGIN", "456")
    monkeypatch.setenv("TRADIN_MT5_PASSWORD", "envpass")

    config = load_config(cfg_path)
    assert config.use_mt5 is True
    assert config.mt5.login == 456
    assert config.mt5.password == "envpass"

