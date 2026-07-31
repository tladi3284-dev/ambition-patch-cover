from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class SupportStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONDITIONAL = "CONDITIONAL"
    UNKNOWN = "UNKNOWN"


class TranslationStatus(str, Enum):
    NOT_TRANSLATED = "NOT_TRANSLATED"
    DRAFT = "DRAFT"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    HISTORY_REVIEWED = "HISTORY_REVIEWED"
    UI_REVIEWED = "UI_REVIEWED"
    APPROVED = "APPROVED"


TRANSLATION_STATUS_ORDER = [
    TranslationStatus.NOT_TRANSLATED,
    TranslationStatus.DRAFT,
    TranslationStatus.REVIEW_REQUIRED,
    TranslationStatus.HISTORY_REVIEWED,
    TranslationStatus.UI_REVIEWED,
    TranslationStatus.APPROVED,
]


@dataclass
class ProjectConfig:
    root: Path
    original_source_path: Path
    workcopy_path: Path
    backup_path: Path
    output_path: Path

    def to_dict(self) -> dict:
        return {
            "original_source_path": str(self.original_source_path),
            "workcopy_path": str(self.workcopy_path),
            "backup_path": str(self.backup_path),
            "output_path": str(self.output_path),
        }

    @staticmethod
    def from_dict(root: Path, data: dict) -> "ProjectConfig":
        return ProjectConfig(
            root=root,
            original_source_path=Path(data["original_source_path"]),
            workcopy_path=Path(data["workcopy_path"]),
            backup_path=Path(data["backup_path"]),
            output_path=Path(data["output_path"]),
        )
