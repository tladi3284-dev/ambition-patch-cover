import pytest

from NOBU_ToolHub.launcher.config_manager import ConfigManager
from NOBU_ToolHub.launcher.game_path_finder import (
    DetectionSource,
    GamePathFinder,
    parse_libraryfolders_vdf,
)

GAME_KEY = "NOBU15_TAISHI_PK"
STEAM_FOLDER = "NOBUNAGAS_AMBITION_TAISHI"


def _finder(tmp_path, config=None):
    config = config or ConfigManager(config_path=tmp_path / "toolhub_config.json")
    return GamePathFinder(
        config,
        steam_common_default=tmp_path / "default_steam" / "steamapps" / "common",
        libraryfolders_vdf=tmp_path / "default_steam" / "steamapps" / "libraryfolders.vdf",
    ), config


def test_locate_finds_via_default_steam_library_first(tmp_path):
    finder, _ = _finder(tmp_path)
    (finder.steam_common_default / STEAM_FOLDER).mkdir(parents=True)

    result = finder.locate(GAME_KEY)

    assert result.found is True
    assert result.source == DetectionSource.STEAM_LIBRARY
    assert result.path == finder.steam_common_default / STEAM_FOLDER


def test_locate_falls_back_to_libraryfolders_vdf(tmp_path):
    finder, _ = _finder(tmp_path)
    extra_library = tmp_path / "D_drive" / "SteamLibrary"
    (extra_library / "steamapps" / "common" / STEAM_FOLDER).mkdir(parents=True)
    finder.libraryfolders_vdf.parent.mkdir(parents=True, exist_ok=True)
    finder.libraryfolders_vdf.write_text(
        '"libraryfolders"\n{\n\t"1"\n\t{\n\t\t"path"\t\t"%s"\n\t}\n}\n'
        % str(extra_library).replace("\\", "\\\\"),
        encoding="utf-8",
    )

    result = finder.locate(GAME_KEY)

    assert result.found is True
    assert result.source == DetectionSource.LIBRARYFOLDERS_VDF
    assert result.path == extra_library / "steamapps" / "common" / STEAM_FOLDER


def test_locate_falls_back_to_user_config(tmp_path):
    finder, config = _finder(tmp_path)
    manual_dir = tmp_path / "manual" / "NOBU15"
    manual_dir.mkdir(parents=True)
    config.set_game_path(GAME_KEY, manual_dir)

    result = finder.locate(GAME_KEY)

    assert result.found is True
    assert result.source == DetectionSource.USER_CONFIG
    assert result.path == manual_dir


def test_locate_requires_manual_selection_when_nothing_found(tmp_path):
    finder, _ = _finder(tmp_path)

    result = finder.locate(GAME_KEY)

    assert result.found is False
    assert result.source == DetectionSource.MANUAL_SELECTION
    assert result.path is None


def test_locate_unknown_game_key_raises(tmp_path):
    finder, _ = _finder(tmp_path)
    with pytest.raises(KeyError):
        finder.locate("NOT_A_GAME")


def test_parse_libraryfolders_vdf_missing_file_returns_empty(tmp_path):
    assert parse_libraryfolders_vdf(tmp_path / "missing.vdf") == []


def test_registry_lookup_is_none_off_windows(tmp_path):
    finder, _ = _finder(tmp_path)
    # This sandbox has no winreg module (non-Windows); the method must
    # degrade to "not found" rather than raising.
    assert finder.find_via_registry(GAME_KEY) is None
