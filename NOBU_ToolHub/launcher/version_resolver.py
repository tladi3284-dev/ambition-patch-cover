"""Version Resolver — 런처 담당 범위 중 Version Selection (Foundation R1, Ⅱ.2나).

하나의 시리즈(예: NOBU14)에 여러 변형(기본판/PK/Ascension 등)이
카탈로그에 등록되어 있을 수 있다(Foundation R1 Ⅲ.7). VersionResolver는
ConfigManager에 실제 경로가 설정된 변형들 중에서 사용할 것을 하나로
확정한다. 여러 변형이 동시에 설정되어 있고 어떤 것을 쓸지 지정되지
않으면, 추측하지 않고 AmbiguousVersionError로 즉시 중단한다
(Governance Ⅱ.1나 Fail-Fast 원칙).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from .config_manager import GAME_CATALOG, ConfigManager, GameCatalogEntry, TrustGrade


class AmbiguousVersionError(Exception):
    """한 시리즈에 둘 이상의 변형이 설정되어 있고 우선순위가 지정되지 않음."""


class UnknownSeriesError(Exception):
    """카탈로그에 없는 시리즈명이 조회됨."""


@dataclass(frozen=True)
class ResolvedVersion:
    series: str
    key: str
    path: Path
    trust_grade: TrustGrade
    note: str


class VersionResolver:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def variants_for_series(self, series: str) -> List[GameCatalogEntry]:
        variants = [e for e in GAME_CATALOG if e.series == series]
        if not variants:
            raise UnknownSeriesError(f"unknown series: {series}")
        return variants

    def configured_variants(self, series: str) -> List[ResolvedVersion]:
        """해당 시리즈 중 ConfigManager에 실제 경로가 설정된 변형만 반환한다."""
        resolved = []
        for entry in self.variants_for_series(series):
            path = self.config_manager.get_game_path(entry.key)
            if path is not None:
                resolved.append(
                    ResolvedVersion(entry.series, entry.key, path, entry.trust_grade, entry.note)
                )
        return resolved

    def resolve(self, series: str, prefer_key: Optional[str] = None) -> Optional[ResolvedVersion]:
        """설정된 변형이 없으면 None(미확정), 하나면 그것, 여럿이면 prefer_key로 선택.

        prefer_key 없이 여럿이 설정되어 있으면 임의로 고르지 않고 예외를 낸다.
        """
        configured = self.configured_variants(series)

        if not configured:
            return None

        if len(configured) == 1:
            return configured[0]

        if prefer_key is not None:
            for resolved in configured:
                if resolved.key == prefer_key:
                    return resolved
            raise UnknownSeriesError(
                f"prefer_key {prefer_key!r} is not a configured variant of series {series!r}"
            )

        raise AmbiguousVersionError(
            f"series {series!r} has {len(configured)} configured variants "
            f"({[r.key for r in configured]}); pass prefer_key to disambiguate"
        )
