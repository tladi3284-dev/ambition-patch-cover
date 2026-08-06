"""Configuration Manager — 런처 담당 범위 중 Configuration (Foundation R1, Ⅱ.2나).

설정 파일은 JSON으로 관리하며, Foundation R1 Ⅲ.6가의 "[Games] 섹션에
NOBU11~NOBU16 경로 키 관리"를 games 딕셔너리로 표현한다. 모든 저장은
Governance Baseline Ⅱ.1가 원본 보호 원칙에 따라 임시파일 작성 후
os.replace()로 원자적 교체한다.
"""

from __future__ import annotations

import json
import os
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

CONFIG_SCHEMA_VERSION = 1
DEFAULT_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEFAULT_CONFIG_FILE = "toolhub_config.json"


class TrustGrade(str, Enum):
    """개별 도구 연동 신뢰등급 (Governance Baseline Ⅲ.2나)."""

    AUTHORITATIVE = "AUTHORITATIVE"  # 원본 그대로 실행 확인됨
    VERIFIED_SINGLE = "VERIFIED_SINGLE"  # 1회 검증
    CANDIDATE = "CANDIDATE"  # 미검증 매핑
    UNTRUSTED = "UNTRUSTED"  # 경로·버전 미확인


@dataclass(frozen=True)
class GameCatalogEntry:
    """Foundation R1 Ⅲ.7 "PC 실제 소장 경로 [확인됨]" 표를 코드로 옮긴 것.

    steam_folder는 Steam library의 steamapps/common/ 하위 폴더명이다.
    trust_grade는 ToolHub가 아직 어떤 도구도 실제 실행 검증하지 않았으므로
    기본값을 CANDIDATE로 둔다 (미확인 내용을 확정처럼 기술하지 않는다).
    """

    key: str
    series: str
    steam_folder: str
    trust_grade: TrustGrade = TrustGrade.CANDIDATE
    note: str = ""


# Foundation R1, Ⅲ.7 (가~사). NOBU01~NOBU10은 미보유(아자)로 등재하지 않는다.
GAME_CATALOG: List[GameCatalogEntry] = [
    GameCatalogEntry("NOBU11_TENKASOUSEI_PK", "NOBU11", "Nobunaga11WPK"),
    GameCatalogEntry(
        "NOBU12_KAKUSHIN_PK", "NOBU12", "NOBUNAGA'S AMBITION Kakushin with Power Up Kit"
    ),
    GameCatalogEntry(
        "NOBU13_TENDO_PK", "NOBU13", "NOBUNAGA'S AMBITION Tendou with Power Up Kit"
    ),
    GameCatalogEntry(
        "NOBU14_SPHERE_OF_INFLUENCE", "NOBU14", "Nobunaga's Ambition Souzou"
    ),
    GameCatalogEntry(
        "NOBU14_SPHERE_OF_INFLUENCE_ASCENSION",
        "NOBU14",
        "NOBUNAGAS_AMBITION_Souzou_SengokuRisshiden",
    ),
    GameCatalogEntry("NOBU15_TAISHI_PK", "NOBU15", "NOBUNAGAS_AMBITION_TAISHI"),
    GameCatalogEntry(
        "NOBU16_PK",
        "NOBU16",
        "NOBU16",
        trust_grade=TrustGrade.CANDIDATE,
        note="CE(Chronicle Edition) 해당 여부 미확인 — 추가 검증 필요 (Foundation R1 Ⅲ.7사)",
    ),
]

GAME_CATALOG_BY_KEY: Dict[str, GameCatalogEntry] = {e.key: e for e in GAME_CATALOG}


def _default_config() -> dict:
    return {
        "schema_version": CONFIG_SCHEMA_VERSION,
        "games": {entry.key: {"path": None} for entry in GAME_CATALOG},
        "tools": {},
        "settings": {},
    }


class ConfigManager:
    """게임 경로 및 도구 설정을 원자적으로 읽고 쓴다."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = Path(config_path) if config_path is not None else (
            DEFAULT_CONFIG_DIR / DEFAULT_CONFIG_FILE
        )
        self._data: Optional[dict] = None

    def load(self) -> dict:
        if self.config_path.exists():
            self._data = json.loads(self.config_path.read_text(encoding="utf-8"))
        else:
            self._data = _default_config()
            self.save(self._data)
        return self._data

    @property
    def data(self) -> dict:
        if self._data is None:
            self.load()
        return self._data

    def save(self, data: Optional[dict] = None) -> None:
        """임시파일 작성 후 os.replace()로 원자적 교체한다 (직접 덮어쓰기 금지)."""
        payload = data if data is not None else self._data
        if payload is None:
            raise ValueError("no config data to save")

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=str(self.config_path.parent), prefix=".toolhub_config_", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, sort_keys=True, ensure_ascii=False)
            os.replace(tmp_path, self.config_path)
        except BaseException:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise
        self._data = payload

    def get_game_path(self, game_key: str) -> Optional[Path]:
        if game_key not in GAME_CATALOG_BY_KEY:
            raise KeyError(f"unknown game key: {game_key}")
        raw = self.data.get("games", {}).get(game_key, {}).get("path")
        return Path(raw) if raw else None

    def set_game_path(self, game_key: str, path: Optional[Path]) -> None:
        if game_key not in GAME_CATALOG_BY_KEY:
            raise KeyError(f"unknown game key: {game_key}")
        data = self.data
        data.setdefault("games", {}).setdefault(game_key, {})["path"] = (
            str(path) if path is not None else None
        )
        self.save(data)

    def get_tool_path(self, tool_name: str) -> Optional[Path]:
        raw = self.data.get("tools", {}).get(tool_name, {}).get("path")
        return Path(raw) if raw else None

    def set_tool_path(self, tool_name: str, path: Optional[Path]) -> None:
        data = self.data
        data.setdefault("tools", {}).setdefault(tool_name, {})["path"] = (
            str(path) if path is not None else None
        )
        self.save(data)
