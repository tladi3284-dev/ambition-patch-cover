"""NOBU ToolHub CLI 진입점 — Phase 1 스켈레톤.

GUI(PyQt6)는 Phase 3 대상이므로(Foundation R1 Ⅳ.2다), Phase 1에서는
Core Engine 4개 모듈을 커맨드라인으로 검증할 수 있는 최소 진입점만
제공한다. python -m NOBU_ToolHub.launcher.main <command> 형태로 실행한다.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config_manager import GAME_CATALOG, ConfigManager
from .game_path_finder import GamePathFinder
from .logger_setup import get_logger, setup_logger
from .tool_manager import KNOWN_TOOLS, TOOL_MAPPING, ToolManager
from .version_resolver import VersionResolver

log = get_logger("main")


def cmd_list_games(args: argparse.Namespace, config: ConfigManager) -> int:
    for entry in GAME_CATALOG:
        path = config.get_game_path(entry.key)
        status = str(path) if path else "(미설정)"
        print(f"{entry.key:40s} series={entry.series:8s} trust={entry.trust_grade.value:16s} path={status}")
    return 0


def cmd_list_tools(args: argparse.Namespace, config: ConfigManager) -> int:
    for series, categories in TOOL_MAPPING.items():
        print(f"{series}: {', '.join(c.value for c in categories)}")
    print()
    for name, tool in KNOWN_TOOLS.items():
        configured = config.get_tool_path(name)
        status = str(configured) if configured else "(미설정)"
        print(f"{name:28s} category={tool.category.value:16s} version={tool.version or '-':10s} path={status}")
    return 0


def cmd_detect(args: argparse.Namespace, config: ConfigManager) -> int:
    finder = GamePathFinder(config)
    result = finder.locate(args.game_key)
    if result.found:
        print(f"{result.game_key}: found via {result.source.value} -> {result.path}")
    else:
        print(f"{result.game_key}: not found automatically (source={result.source.value}); manual selection required")
    return 0 if result.found else 1


def cmd_set_path(args: argparse.Namespace, config: ConfigManager) -> int:
    config.set_game_path(args.game_key, Path(args.path))
    print(f"{args.game_key} -> {args.path}")
    return 0


def cmd_resolve_version(args: argparse.Namespace, config: ConfigManager) -> int:
    resolver = VersionResolver(config)
    resolved = resolver.resolve(args.series, prefer_key=args.prefer)
    if resolved is None:
        print(f"{args.series}: no configured variant yet")
        return 1
    print(f"{args.series}: resolved={resolved.key} trust={resolved.trust_grade.value} path={resolved.path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="NOBU_ToolHub", description="NOBU ToolHub launcher CLI (Phase 1 skeleton)")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-games", help="등록된 게임 카탈로그와 설정된 경로 출력").set_defaults(func=cmd_list_games)
    sub.add_parser("list-tools", help="시리즈별 도구 매핑과 등록된 도구 출력").set_defaults(func=cmd_list_tools)

    p_detect = sub.add_parser("detect", help="5단계 자동 감지로 게임 경로 탐색")
    p_detect.add_argument("game_key")
    p_detect.set_defaults(func=cmd_detect)

    p_set = sub.add_parser("set-path", help="게임 경로를 수동으로 설정")
    p_set.add_argument("game_key")
    p_set.add_argument("path")
    p_set.set_defaults(func=cmd_set_path)

    p_resolve = sub.add_parser("resolve-version", help="시리즈 내 설정된 변형을 확정")
    p_resolve.add_argument("series")
    p_resolve.add_argument("--prefer", default=None)
    p_resolve.set_defaults(func=cmd_resolve_version)

    return parser


def main(argv=None) -> int:
    setup_logger()
    parser = build_parser()
    args = parser.parse_args(argv)
    config = ConfigManager()
    return args.func(args, config)


if __name__ == "__main__":
    sys.exit(main())
