import json
from pathlib import Path

from ._util import is_within
from .models import ProjectConfig

PROJECT_FILE_NAME = "project.json"


class ProjectPathConflictError(Exception):
    """workcopy_path is, or is nested inside, original_source_path."""


def create_project(root: Path, original_source_path: Path, workcopy_path: Path,
                    backup_path: Path, output_path: Path) -> ProjectConfig:
    """
    Enforces safety principle #2 (작업 사본 분리): workcopy_path must never be
    original_source_path itself or a descendant of it, otherwise a workcopy
    rebuild could silently write into the read-only Steam install.
    """
    original_source_path = Path(original_source_path).resolve()
    workcopy_path = Path(workcopy_path)

    if workcopy_path.resolve() == original_source_path or is_within(workcopy_path, original_source_path):
        raise ProjectPathConflictError(
            f"workcopy_path {workcopy_path} must not be inside original_source_path {original_source_path}"
        )

    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    config = ProjectConfig(
        root=root,
        original_source_path=original_source_path,
        workcopy_path=workcopy_path,
        backup_path=Path(backup_path),
        output_path=Path(output_path),
    )
    save_project(config)
    return config


def save_project(config: ProjectConfig) -> Path:
    project_file = config.root / PROJECT_FILE_NAME
    project_file.write_text(json.dumps(config.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return project_file


def load_project(root: Path) -> ProjectConfig:
    root = Path(root)
    project_file = root / PROJECT_FILE_NAME
    if not project_file.exists():
        raise FileNotFoundError(f"no project.json under {root}; run project-init first")
    data = json.loads(project_file.read_text(encoding="utf-8"))
    return ProjectConfig.from_dict(root, data)
