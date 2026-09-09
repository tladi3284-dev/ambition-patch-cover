"""Game Path Finder — 런처 담당 범위 중 Path Management (Foundation R1, Ⅱ.2나).

Foundation R1 Ⅲ.5가에 명시된 5단계 자동 감지 순서를 그대로 구현한다:
  1) Steam Library(기본 설치 경로) → 2) Steam libraryfolders.vdf →
  3) Registry → 4) User Config → 5) Manual Selection

각 단계는 독립적으로 테스트 가능하도록 순수 함수/명시적 인자 형태로
작성했고, locate()가 이를 순서대로 시도한다. 레지스트리 조회는
Windows 전용이므로 winreg 모듈이 없으면 조용히 건너뛴다(플랫폼별
Fail-Fast가 아니라 "해당 없음"으로 취급— 이는 오류가 아니다).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional

from .config_manager import GAME_CATALOG_BY_KEY, ConfigManager

DEFAULT_STEAM_COMMON_WINDOWS = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common"
)
DEFAULT_STEAM_LIBRARYFOLDERS_VDF = Path(
    r"C:\Program Files (x86)\Steam\steamapps\libraryfolders.vdf"
)
STEAM_REGISTRY_KEY = r"SOFTWARE\WOW6432Node\Valve\Steam"
STEAM_REGISTRY_VALUE = "InstallPath"

_VDF_PATH_RE = re.compile(r'"path"\s*"([^"]+)"', re.IGNORECASE)


class DetectionSource(str, Enum):
    STEAM_LIBRARY = "STEAM_LIBRARY"
    LIBRARYFOLDERS_VDF = "LIBRARYFOLDERS_VDF"
    REGISTRY = "REGISTRY"
    USER_CONFIG = "USER_CONFIG"
    MANUAL_SELECTION = "MANUAL_SELECTION"


@dataclass(frozen=True)
class PathLookupResult:
    game_key: str
    path: Optional[Path]
    source: DetectionSource
    found: bool


def parse_libraryfolders_vdf(vdf_path: Path) -> List[Path]:
    """libraryfolders.vdf에서 "path" 값을 모두 추출한다 (Valve KeyValues 간이 파서).

    완전한 VDF 파서가 아니라 "path" 키의 문자열 값만 정규식으로 뽑아낸다.
    추가 의존성(vdf 패키지 등) 없이 Foundation R1 Ⅲ.5나 요구를 충족한다.
    """
    if not vdf_path.exists():
        return []
    text = vdf_path.read_text(encoding="utf-8", errors="replace")
    roots = []
    for match in _VDF_PATH_RE.finditer(text):
        raw = match.group(1).replace("\\\\", "\\")
        roots.append(Path(raw) / "steamapps" / "common")
    return roots


class GamePathFinder:
    def __init__(
        self,
        config_manager: ConfigManager,
        steam_common_default: Path = DEFAULT_STEAM_COMMON_WINDOWS,
        libraryfolders_vdf: Path = DEFAULT_STEAM_LIBRARYFOLDERS_VDF,
    ):
        self.config_manager = config_manager
        self.steam_common_default = Path(steam_common_default)
        self.libraryfolders_vdf = Path(libraryfolders_vdf)

    def find_via_steam_library(self, game_key: str) -> Optional[Path]:
        """1) 단계: 기본 Steam 라이브러리(steamapps/common) 직속 폴더."""
        entry = GAME_CATALOG_BY_KEY[game_key]
        candidate = self.steam_common_default / entry.steam_folder
        return candidate if candidate.is_dir() else None

    def find_via_libraryfolders_vdf(self, game_key: str) -> Optional[Path]:
        """2) 단계: libraryfolders.vdf에 등록된 추가 Steam 라이브러리."""
        entry = GAME_CATALOG_BY_KEY[game_key]
        for root in parse_libraryfolders_vdf(self.libraryfolders_vdf):
            candidate = root / entry.steam_folder
            if candidate.is_dir():
                return candidate
        return None

    def find_via_registry(self, game_key: str) -> Optional[Path]:
        """3) 단계: Windows Registry에서 Steam 설치 위치를 조회한다."""
        try:
            import winreg
        except ImportError:
            return None

        entry = GAME_CATALOG_BY_KEY[game_key]
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, STEAM_REGISTRY_KEY) as key:
                install_path, _ = winreg.QueryValueEx(key, STEAM_REGISTRY_VALUE)
        except OSError:
            return None

        candidate = Path(install_path) / "steamapps" / "common" / entry.steam_folder
        return candidate if candidate.is_dir() else None

    def find_via_user_config(self, game_key: str) -> Optional[Path]:
        """4) 단계: 사용자가 ConfigManager에 직접 지정한 경로."""
        path = self.config_manager.get_game_path(game_key)
        return path if path and path.is_dir() else None

    def locate(self, game_key: str) -> PathLookupResult:
        """5단계를 순서대로 시도하고 가장 먼저 발견된 경로를 반환한다.

        아무 단계에서도 찾지 못하면 MANUAL_SELECTION 소스로 found=False를
        반환한다 — 경로를 추측하지 않는다(Governance Ⅳ.2가 금지 사항).
        """
        if game_key not in GAME_CATALOG_BY_KEY:
            raise KeyError(f"unknown game key: {game_key}")

        steam_path = self.find_via_steam_library(game_key)
        if steam_path is not None:
            return PathLookupResult(game_key, steam_path, DetectionSource.STEAM_LIBRARY, True)

        vdf_path = self.find_via_libraryfolders_vdf(game_key)
        if vdf_path is not None:
            return PathLookupResult(game_key, vdf_path, DetectionSource.LIBRARYFOLDERS_VDF, True)

        registry_path = self.find_via_registry(game_key)
        if registry_path is not None:
            return PathLookupResult(game_key, registry_path, DetectionSource.REGISTRY, True)

        user_path = self.find_via_user_config(game_key)
        if user_path is not None:
            return PathLookupResult(game_key, user_path, DetectionSource.USER_CONFIG, True)

        return PathLookupResult(game_key, None, DetectionSource.MANUAL_SELECTION, False)
