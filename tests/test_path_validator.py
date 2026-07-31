from localizer import path_validator


def test_validate_missing_root_reports_not_ok(tmp_path):
    result = path_validator.validate_game_root(tmp_path / "does_not_exist")
    assert not result.ok
    assert any("does not exist" in w for w in result.warnings)


def test_validate_root_without_subfolders_warns(tmp_path):
    root = tmp_path / "game"
    root.mkdir()
    result = path_validator.validate_game_root(root)
    assert result.ok
    assert not result.msg_dir_found
    assert "msg/ subfolder not found" in result.warnings
    assert "res/ subfolder not found" in result.warnings
    assert "grp/ subfolder not found" in result.warnings


def test_validate_root_with_subfolders_has_no_warnings(tmp_path):
    root = tmp_path / "game"
    (root / "msg").mkdir(parents=True)
    (root / "res").mkdir()
    (root / "grp").mkdir()
    result = path_validator.validate_game_root(root)
    assert result.ok
    assert result.msg_dir_found
    assert result.res_dir_found
    assert result.grp_dir_found
    assert result.warnings == []


def test_validate_root_that_is_a_file(tmp_path):
    file_path = tmp_path / "not_a_dir"
    file_path.write_text("x")
    result = path_validator.validate_game_root(file_path)
    assert not result.ok
    assert any("is not a directory" in w for w in result.warnings)
