"""Logging Framework — 런처 담당 범위 중 Logging (Foundation R1, Ⅱ.2나).

중앙화 대상 로그(Foundation R1, Ⅱ.4가)를 NOBU_ToolHub/logs/ 아래 단일
회전 로그 파일 + 콘솔로 출력한다. 여러 모듈이 반복 호출해도 핸들러가
중복 부착되지 않도록 멱등적으로 동작한다.
"""

from __future__ import annotations

import logging
import logging.handlers
from pathlib import Path
from typing import Optional

DEFAULT_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
DEFAULT_LOG_FILE = "toolhub.log"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_ROOT_LOGGER_NAME = "nobu_toolhub"
_configured = False


def setup_logger(
    log_dir: Optional[Path] = None,
    level: int = logging.INFO,
    max_bytes: int = 1_000_000,
    backup_count: int = 5,
) -> logging.Logger:
    """루트 ToolHub 로거를 1회만 구성하고 반환한다. 재호출 시 기존 핸들러를 재사용한다."""
    global _configured
    root = logging.getLogger(_ROOT_LOGGER_NAME)

    if _configured:
        return root

    log_dir = Path(log_dir) if log_dir is not None else DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    file_handler = logging.handlers.RotatingFileHandler(
        log_dir / DEFAULT_LOG_FILE,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root.setLevel(level)
    root.addHandler(file_handler)
    root.addHandler(console_handler)
    root.propagate = False

    _configured = True
    return root


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """setup_logger()가 아직 호출되지 않았다면 기본 설정으로 자동 구성한다."""
    setup_logger()
    if name:
        return logging.getLogger(f"{_ROOT_LOGGER_NAME}.{name}")
    return logging.getLogger(_ROOT_LOGGER_NAME)
