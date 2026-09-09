import logging

from NOBU_ToolHub.launcher import logger_setup


def test_setup_logger_creates_log_dir_and_file(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_setup, "_configured", False)
    log_dir = tmp_path / "logs"

    logger = logger_setup.setup_logger(log_dir=log_dir)
    logger.info("hello from test")
    for handler in logger.handlers:
        handler.flush()

    assert (log_dir / logger_setup.DEFAULT_LOG_FILE).exists()


def test_setup_logger_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(logger_setup, "_configured", False)
    logger_first = logger_setup.setup_logger(log_dir=tmp_path / "logs")
    handler_count_first = len(logger_first.handlers)

    logger_second = logger_setup.setup_logger(log_dir=tmp_path / "logs_other")

    assert logger_second is logger_first
    assert len(logger_second.handlers) == handler_count_first


def test_get_logger_returns_child_logger(monkeypatch):
    monkeypatch.setattr(logger_setup, "_configured", False)
    child = logger_setup.get_logger("config_manager")
    assert child.name == "nobu_toolhub.config_manager"
    assert isinstance(child, logging.Logger)
