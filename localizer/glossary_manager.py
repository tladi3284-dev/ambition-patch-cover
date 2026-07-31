import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


class GlossaryConflictError(Exception):
    pass


@dataclass
class GlossaryEntry:
    japanese: str
    korean: str
    category: Optional[str] = None

    def to_dict(self) -> dict:
        return {"japanese": self.japanese, "korean": self.korean, "category": self.category}

    @staticmethod
    def from_dict(data: dict) -> "GlossaryEntry":
        return GlossaryEntry(japanese=data["japanese"], korean=data["korean"], category=data.get("category"))


class GlossaryManager:
    def __init__(self, entries: Optional[Dict[str, GlossaryEntry]] = None):
        self.entries: Dict[str, GlossaryEntry] = entries or {}

    def add(self, japanese: str, korean: str, category: Optional[str] = None,
            allow_overwrite: bool = False) -> GlossaryEntry:
        existing = self.entries.get(japanese)
        if existing is not None and existing.korean != korean and not allow_overwrite:
            raise GlossaryConflictError(
                f"{japanese!r} already mapped to {existing.korean!r}; refusing to overwrite with {korean!r}"
            )
        entry = GlossaryEntry(japanese=japanese, korean=korean, category=category)
        self.entries[japanese] = entry
        return entry

    def remove(self, japanese: str) -> None:
        self.entries.pop(japanese, None)

    def get(self, japanese: str) -> Optional[GlossaryEntry]:
        return self.entries.get(japanese)

    def all(self) -> List[GlossaryEntry]:
        return list(self.entries.values())

    def save(self, path: Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = [e.to_dict() for e in self.entries.values()]
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    @staticmethod
    def load(path: Path) -> "GlossaryManager":
        path = Path(path)
        if not path.exists():
            return GlossaryManager()
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = {d["japanese"]: GlossaryEntry.from_dict(d) for d in data}
        return GlossaryManager(entries)
