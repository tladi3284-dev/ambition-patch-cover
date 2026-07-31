import shutil
from pathlib import Path

from ._util import is_within
from .baseline_manager import build_manifest
from .project_manager import ProjectPathConflictError


class WorkcopyExistsError(Exception):
    pass


class WorkcopyHashMismatchError(Exception):
    pass


def make_workcopy(original_source_path: Path, workcopy_path: Path, allow_existing: bool = False) -> Path:
    """
    Copies original_source_path -> workcopy_path, then re-hashes both trees
    and refuses to report success unless every file matches (principle #5:
    deterministic build; principle #1: original stays read-only — this
    function only ever reads from it, never writes back).
    """
    original_source_path = Path(original_source_path).resolve()
    workcopy_path = Path(workcopy_path)

    if workcopy_path.resolve() == original_source_path or is_within(workcopy_path, original_source_path):
        raise ProjectPathConflictError(
            f"workcopy_path {workcopy_path} must not be inside original_source_path {original_source_path}"
        )

    if workcopy_path.exists():
        if not allow_existing:
            raise WorkcopyExistsError(f"{workcopy_path} already exists; pass allow_existing=True to overwrite")
        shutil.rmtree(workcopy_path)

    shutil.copytree(original_source_path, workcopy_path)

    original_manifest = build_manifest(original_source_path)
    workcopy_manifest = build_manifest(workcopy_path)
    if original_manifest != workcopy_manifest:
        mismatched = sorted(
            k for k in set(original_manifest) | set(workcopy_manifest)
            if original_manifest.get(k) != workcopy_manifest.get(k)
        )
        raise WorkcopyHashMismatchError(f"post-copy hash mismatch for: {mismatched}")

    return workcopy_path
