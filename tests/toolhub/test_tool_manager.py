import stat
import sys

import pytest

from NOBU_ToolHub.launcher.config_manager import ConfigManager
from NOBU_ToolHub.launcher.tool_manager import (
    TOOL_MAPPING,
    ToolCategory,
    ToolManager,
    ToolNotConfiguredError,
)


def _manager(tmp_path):
    config = ConfigManager(config_path=tmp_path / "toolhub_config.json")
    return ToolManager(config), config


def test_tool_mapping_matches_foundation_r1_iii_6():
    assert TOOL_MAPPING["NOBU11"] == [
        ToolCategory.MSG_EDITOR,
        ToolCategory.FONT_TOOL,
        ToolCategory.RESOURCE_TOOL,
    ]
    assert TOOL_MAPPING["NOBU16"] == [ToolCategory.MSG_EDITOR, ToolCategory.RESOURCE_TOOL]


def test_tools_for_unknown_series_raises(tmp_path):
    manager, _ = _manager(tmp_path)
    with pytest.raises(KeyError):
        manager.tools_for_series("NOBU99")


def test_tools_by_category_returns_both_picture_tools(tmp_path):
    manager, _ = _manager(tmp_path)
    picture_tools = manager.tools_by_category(ToolCategory.PICTURE_TOOL)
    assert {t.name for t in picture_tools} == {"picture_editor", "picture_editor_extended"}


def test_launch_without_configured_path_raises(tmp_path):
    manager, _ = _manager(tmp_path)
    with pytest.raises(ToolNotConfiguredError):
        manager.launch("message_editor")


def test_launch_unknown_tool_raises_keyerror(tmp_path):
    manager, _ = _manager(tmp_path)
    with pytest.raises(KeyError):
        manager.launch("not_a_real_tool")


def test_launch_with_missing_executable_file_raises(tmp_path):
    manager, config = _manager(tmp_path)
    config.set_tool_path("message_editor", tmp_path / "does_not_exist.exe")
    with pytest.raises(ToolNotConfiguredError):
        manager.launch("message_editor")


@pytest.mark.skipif(sys.platform == "win32", reason="uses a POSIX shebang script as a stand-in executable")
def test_launch_spawns_independent_process(tmp_path):
    manager, config = _manager(tmp_path)
    script = tmp_path / "fake_message_editor.sh"
    script.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IEXEC)
    config.set_tool_path("message_editor", script)

    proc = manager.launch("message_editor")
    returncode = proc.wait(timeout=5)

    assert returncode == 0
