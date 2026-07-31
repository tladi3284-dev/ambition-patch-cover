import pytest

from localizer import workcopy_creator
from localizer.project_manager import ProjectPathConflictError


def test_make_workcopy_copies_and_verifies(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    (original / "a.txt").write_bytes(b"hello")
    (original / "sub").mkdir()
    (original / "sub" / "b.txt").write_bytes(b"world")

    workcopy = tmp_path / "workcopy"
    result = workcopy_creator.make_workcopy(original, workcopy)

    assert result == workcopy
    assert (workcopy / "a.txt").read_bytes() == b"hello"
    assert (workcopy / "sub" / "b.txt").read_bytes() == b"world"


def test_make_workcopy_rejects_nested_path(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    with pytest.raises(ProjectPathConflictError):
        workcopy_creator.make_workcopy(original, original / "nested_workcopy")


def test_make_workcopy_refuses_existing_without_flag(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    (original / "a.txt").write_bytes(b"hello")
    workcopy = tmp_path / "workcopy"
    workcopy.mkdir()

    with pytest.raises(workcopy_creator.WorkcopyExistsError):
        workcopy_creator.make_workcopy(original, workcopy)


def test_make_workcopy_allows_existing_with_flag(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    (original / "a.txt").write_bytes(b"hello")
    workcopy = tmp_path / "workcopy"
    workcopy.mkdir()
    (workcopy / "stale.txt").write_bytes(b"old")

    result = workcopy_creator.make_workcopy(original, workcopy, allow_existing=True)
    assert (result / "a.txt").read_bytes() == b"hello"
    assert not (result / "stale.txt").exists()


def test_original_source_is_never_written(tmp_path):
    original = tmp_path / "original"
    original.mkdir()
    (original / "a.txt").write_bytes(b"hello")
    before = (original / "a.txt").stat().st_mtime_ns

    workcopy_creator.make_workcopy(original, tmp_path / "workcopy")

    after = (original / "a.txt").stat().st_mtime_ns
    assert before == after
