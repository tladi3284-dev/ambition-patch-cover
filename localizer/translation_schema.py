"""
Translation corpus with a strict state gate (CLAUDE_CODE_SPEC.md principle 4):
NOT_TRANSLATED -> DRAFT -> REVIEW_REQUIRED -> HISTORY_REVIEWED -> UI_REVIEWED -> APPROVED
Skipping ahead or moving backward is rejected. Only APPROVED entries may be
used as rebuild input (callers should filter via approved_entries()).
"""
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from .models import TRANSLATION_STATUS_ORDER, TranslationStatus

CONTROL_CODE_PATTERN = re.compile(r"\{[^}]*\}|%[sd]|\\n")


class InvalidStatusTransitionError(Exception):
    pass


class ControlCodeLossError(Exception):
    pass


@dataclass
class TranslationEntry:
    logical_id: str
    source_japanese: str
    translated_korean: str = ""
    status: TranslationStatus = TranslationStatus.NOT_TRANSLATED
    category: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "logical_id": self.logical_id,
            "source_japanese": self.source_japanese,
            "translated_korean": self.translated_korean,
            "status": self.status.value,
            "category": self.category,
        }

    @staticmethod
    def from_dict(data: dict) -> "TranslationEntry":
        return TranslationEntry(
            logical_id=data["logical_id"],
            source_japanese=data["source_japanese"],
            translated_korean=data.get("translated_korean", ""),
            status=TranslationStatus(data.get("status", TranslationStatus.NOT_TRANSLATED.value)),
            category=data.get("category"),
        )


def _extract_control_codes(text: str) -> List[str]:
    return CONTROL_CODE_PATTERN.findall(text)


def validate_transition(current: TranslationStatus, new: TranslationStatus) -> None:
    current_idx = TRANSLATION_STATUS_ORDER.index(current)
    new_idx = TRANSLATION_STATUS_ORDER.index(new)
    if new_idx != current_idx + 1:
        next_name = (
            TRANSLATION_STATUS_ORDER[current_idx + 1].value
            if current_idx + 1 < len(TRANSLATION_STATUS_ORDER)
            else "none"
        )
        raise InvalidStatusTransitionError(
            f"cannot move status from {current.value} to {new.value}; only {next_name} is allowed next"
        )


class TranslationCorpus:
    def __init__(self, entries: Optional[Dict[str, TranslationEntry]] = None):
        self.entries: Dict[str, TranslationEntry] = entries or {}

    def add_entry(self, logical_id: str, source_japanese: str, category: Optional[str] = None) -> TranslationEntry:
        entry = TranslationEntry(logical_id=logical_id, source_japanese=source_japanese, category=category)
        self.entries[logical_id] = entry
        return entry

    def set_translation(self, logical_id: str, translated_korean: str) -> TranslationEntry:
        entry = self.entries[logical_id]
        entry.translated_korean = translated_korean
        return entry

    def advance_status(self, logical_id: str, new_status: TranslationStatus) -> TranslationEntry:
        entry = self.entries[logical_id]
        validate_transition(entry.status, new_status)

        if new_status == TranslationStatus.APPROVED:
            source_codes = sorted(_extract_control_codes(entry.source_japanese))
            translated_codes = sorted(_extract_control_codes(entry.translated_korean))
            if source_codes != translated_codes:
                raise ControlCodeLossError(
                    f"{logical_id}: control codes differ between source {source_codes} "
                    f"and translation {translated_codes}"
                )

        entry.status = new_status
        return entry

    def approved_entries(self) -> Dict[str, TranslationEntry]:
        return {k: v for k, v in self.entries.items() if v.status == TranslationStatus.APPROVED}

    def status_counts(self) -> Dict[str, int]:
        counts = {s.value: 0 for s in TranslationStatus}
        for entry in self.entries.values():
            counts[entry.status.value] += 1
        return counts

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.to_dict() for e in self.entries.values()]
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "TranslationCorpus":
        path = Path(path)
        if not path.exists():
            return TranslationCorpus()
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = {d["logical_id"]: TranslationEntry.from_dict(d) for d in data}
        return TranslationCorpus(entries)
