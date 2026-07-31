import pytest

from localizer import project_manager
from localizer.project_manager import ProjectPathConflictError


def test_create_project_rejects_workcopy_inside_original(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    workcopy = original / "workcopy"

    with pytest.raises(ProjectPathConflictError):
        project_manager.create_project(
            root=tmp_path / "proj",
            original_source_path=original,
            workcopy_path=workcopy,
            backup_path=tmp_path / "backup",
            output_path=tmp_path / "output",
        )


def test_create_project_rejects_workcopy_equal_to_original(tmp_path):
    original = tmp_path / "original"
    original.mkdir()

    with pytest.raises(ProjectPathConflictError):
        project_manager.create_project(
            root=tmp_path / "proj",
            original_source_path=original,
            workcopy_path=original,
            backup_path=tmp_path / "backup",
            output_path=tmp_path / "output",
        )


def test_create_and_load_project_roundtrip(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    config = project_manager.create_project(
        root=tmp_path / "proj",
        original_source_path=original,
        workcopy_path=tmp_path / "workcopy",
        backup_path=tmp_path / "backup",
        output_path=tmp_path / "output",
    )
    loaded = project_manager.load_project(tmp_path / "proj")
    assert loaded.original_source_path == config.original_source_path
    assert loaded.workcopy_path == config.workcopy_path
    assert loaded.backup_path == config.backup_path
    assert loaded.output_path == config.output_path


def test_load_project_missing_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        project_manager.load_project(tmp_path / "nope")
