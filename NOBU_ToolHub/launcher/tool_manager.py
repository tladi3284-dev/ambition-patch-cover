"""Tool Manager — 런처 담당 범위 중 Tool Discovery (Foundation R1, Ⅱ.2나).

런처는 Wrapper 역할만 수행한다(Foundation R1 Ⅱ.2가): 각 도구의 원본
실행 파일은 절대 수정하지 않고, 독립 프로세스로 실행만 시킨다.
게임 시리즈 ↔ 도구 카테고리 매핑은 Foundation R1 Ⅲ.6나를, 확인된
도구 목록은 Ⅲ.1을 그대로 코드로 옮긴 것이다. Font Tool/Resource
Tool은 매핑표에는 등장하지만 Ⅲ.1에 구체적 실행 파일이 명시되지
않았으므로, 카테고리만 등록하고 executable을 임의로 지어내지 않는다.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .config_manager import ConfigManager, TrustGrade
from .logger_setup import get_logger

_log = get_logger("tool_manager")


class ToolCategory(str, Enum):
    MSG_EDITOR = "msg_editor"
    PICTURE_TOOL = "picture_tool"
    FONT_TOOL = "font_tool"
    RESOURCE_TOOL = "resource_tool"


# Foundation R1, Ⅲ.6나 (1~6). 시리즈별로 필요한 도구 카테고리 목록.
TOOL_MAPPING: Dict[str, List[ToolCategory]] = {
    "NOBU11": [ToolCategory.MSG_EDITOR, ToolCategory.FONT_TOOL, ToolCategory.RESOURCE_TOOL],
    "NOBU12": [ToolCategory.MSG_EDITOR, ToolCategory.PICTURE_TOOL],
    "NOBU13": [ToolCategory.MSG_EDITOR, ToolCategory.PICTURE_TOOL],
    "NOBU14": [ToolCategory.PICTURE_TOOL, ToolCategory.MSG_EDITOR, ToolCategory.RESOURCE_TOOL],
    "NOBU15": [ToolCategory.MSG_EDITOR, ToolCategory.PICTURE_TOOL, ToolCategory.RESOURCE_TOOL],
    "NOBU16": [ToolCategory.MSG_EDITOR, ToolCategory.RESOURCE_TOOL],
}


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    category: ToolCategory
    engine: str  # "dotnet_exe" | "python_cli_gui" | "unknown"
    version: Optional[str]
    trust_grade: TrustGrade
    note: str = ""


# Foundation R1, Ⅲ.1 (가~다). 실측 확인된 도구만 등록한다.
KNOWN_TOOLS: Dict[str, ToolDefinition] = {
    "picture_editor": ToolDefinition(
        name="picture_editor",
        category=ToolCategory.PICTURE_TOOL,
        engine="unknown",
        version="1.20",
        trust_grade=TrustGrade.CANDIDATE,
        note="공용 Plugins 사용",
    ),
    "picture_editor_extended": ToolDefinition(
        name="picture_editor_extended",
        category=ToolCategory.PICTURE_TOOL,
        engine="python_cli_gui",
        version="1.24_HAN",
        trust_grade=TrustGrade.CANDIDATE,
        note="Python 기반(CLI+GUI), 공용 Plugins 사용",
    ),
    "message_editor": ToolDefinition(
        name="message_editor",
        category=ToolCategory.MSG_EDITOR,
        engine="dotnet_exe",
        version=None,
        trust_grade=TrustGrade.CANDIDATE,
        note="C#/Windows Forms, SJIS Table 기반, 독립 구조",
    ),
}


class ToolNotConfiguredError(Exception):
    """실행 파일 경로가 ConfigManager에 아직 설정되지 않음."""


class ToolManager:
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def tools_for_series(self, series: str) -> List[ToolCategory]:
        if series not in TOOL_MAPPING:
            raise KeyError(f"unknown series: {series}")
        return list(TOOL_MAPPING[series])

    def tools_by_category(self, category: ToolCategory) -> List[ToolDefinition]:
        return [t for t in KNOWN_TOOLS.values() if t.category == category]

    def resolve_executable(self, tool_name: str) -> Optional[Path]:
        if tool_name not in KNOWN_TOOLS:
            raise KeyError(f"unknown tool: {tool_name}")
        return self.config_manager.get_tool_path(tool_name)

    def launch(
        self,
        tool_name: str,
        args: Optional[List[str]] = None,
        cwd: Optional[Path] = None,
    ) -> subprocess.Popen:
        """도구를 독립 프로세스로 실행한다. 원본 파일은 절대 수정하지 않는다.

        실행 파일 경로가 설정되지 않았으면 추측하지 않고 즉시 실패한다
        (Governance Ⅱ.1나 Fail-Fast).
        """
        if tool_name not in KNOWN_TOOLS:
            raise KeyError(f"unknown tool: {tool_name}")

        executable = self.resolve_executable(tool_name)
        if executable is None:
            raise ToolNotConfiguredError(
                f"tool {tool_name!r} has no configured executable path"
            )
        if not executable.exists():
            raise ToolNotConfiguredError(
                f"configured executable for {tool_name!r} does not exist: {executable}"
            )

        command = [str(executable)] + list(args or [])
        launch_cwd = Path(cwd) if cwd is not None else executable.parent

        _log.info("launching tool=%s command=%s cwd=%s", tool_name, command, launch_cwd)
        return subprocess.Popen(command, cwd=str(launch_cwd))
