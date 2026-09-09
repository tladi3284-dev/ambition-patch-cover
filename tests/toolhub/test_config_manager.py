import json

import pytest

from NOBU_ToolHub.launcher.config_manager import (
    GAME_CATALOG,
    GAME_CATALOG_BY_KEY,
    ConfigManager,
    TrustGrade,
)


def test_game_catalog_has_seven_entries_matching_foundation_r1():
    assert len(GAME_CATALOG) == 7
    assert set(e.key for e in GAME_CATALOG) == {
        "NOBU11_TENKASOUSEI_PK",
        "NOBU12_KAKUSHIN_PK",
        "NOBU13_TENDO_PK",
        "NOBU14_SPHERE_OF_INFLUENCE",
        "NOBU14_SPHERE_OF_INFLUENCE_ASCENSION",
        "NOBU15_TAISHI_PK",
        "NOBU16_PK",
    }


def test_nobu16_defaults_to_candidate_with_ce_note():
    entry = GAME_CATALOG_BY_KEY["NOBU16_PK"]
    assert entry.trust_grade == TrustGrade.CANDIDATE
    assert "CE" in entry.note


def test_load_creates_default_config_on_missing_file(tmp_path):
    config_path = tmp_path / "config" / "toolhub_config.json"
    manager = ConfigManager(config_path=config_path)

    data = manager.load()

    assert config_path.exists()
    assert data["schema_version"] == 1
    assert set(data["games"]) == set(GAME_CATALOG_BY_KEY)
    assert all(v["path"] is None for v in data["games"].values())


def test_set_and_get_game_path_roundtrip(tmp_path):
    manager = ConfigManager(config_path=tmp_path / "toolhub_config.json")
    manager.set_game_path("NOBU15_TAISHI_PK", tmp_path / "games" / "NOBU15")

    assert manager.get_game_path("NOBU15_TAISHI_PK") == tmp_path / "games" / "NOBU15"


def test_get_game_path_unknown_key_raises(tmp_path):
    manager = ConfigManager(config_path=tmp_path / "toolhub_config.json")
    with pytest.raises(KeyError):
        manager.get_game_path("NOT_A_GAME")


def test_save_is_atomic_no_tmp_file_left_behind(tmp_path):
    config_dir = tmp_path / "config"
    manager = ConfigManager(config_path=config_dir / "toolhub_config.json")
    manager.set_game_path("NOBU11_TENKASOUSEI_PK", tmp_path / "g")

    leftovers = list(config_dir.glob(".toolhub_config_*"))
    assert leftovers == []


def test_saved_file_is_valid_json_sorted_keys(tmp_path):
    config_path = tmp_path / "toolhub_config.json"
    manager = ConfigManager(config_path=config_path)
    manager.load()

    raw = config_path.read_text(encoding="utf-8")
    parsed = json.loads(raw)
    assert parsed["schema_version"] == 1


def test_tool_path_roundtrip(tmp_path):
    manager = ConfigManager(config_path=tmp_path / "toolhub_config.json")
    manager.set_tool_path("message_editor", tmp_path / "tools" / "MsgEditor.exe")

    assert manager.get_tool_path("message_editor") == tmp_path / "tools" / "MsgEditor.exe"
    assert manager.get_tool_path("never_configured") is None
