import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


def _sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_manifest(source_root: Path) -> Dict[str, str]:
    source_root = Path(source_root)
    manifest = {}
    for path in sorted(source_root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(source_root).as_posix()
            manifest[rel] = _sha256_of_file(path)
    return manifest


def save_manifest(manifest: Dict[str, str], manifest_path: Path) -> None:
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def load_manifest(manifest_path: Path) -> Dict[str, str]:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


@dataclass
class ManifestDiff:
    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    changed: List[str] = field(default_factory=list)
    unchanged_count: int = 0

    @property
    def unexpected_changes(self) -> int:
        return len(self.added) + len(self.removed) + len(self.changed)


def diff_manifests(baseline: Dict[str, str], current: Dict[str, str]) -> ManifestDiff:
    baseline_files = set(baseline)
    current_files = set(current)
    added = sorted(current_files - baseline_files)
    removed = sorted(baseline_files - current_files)
    changed = sorted(f for f in (baseline_files & current_files) if baseline[f] != current[f])
    unchanged = len(baseline_files & current_files) - len(changed)
    return ManifestDiff(added=added, removed=removed, changed=changed, unchanged_count=unchanged)
