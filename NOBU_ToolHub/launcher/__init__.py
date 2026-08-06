"""NOBU ToolHub Launcher — Phase 1 Core Engine (Foundation R1 / Governance Baseline).

Foundation R1 Ⅲ.2 아키텍처: NOBU ToolHub -> Launcher(Tool Manager /
Configuration Manager / Version Resolver / Game Path Finder) ->
Picture/Message/Resource Tools -> 원본 실행 파일.
"""

from .config_manager import (
    GAME_CATALOG,
    GAME_CATALOG_BY_KEY,
    ConfigManager,
    GameCatalogEntry,
    TrustGrade,
)
from .game_path_finder import DetectionSource, GamePathFinder, PathLookupResult
from .logger_setup import get_logger, setup_logger
from .tool_manager import (
    KNOWN_TOOLS,
    TOOL_MAPPING,
    ToolCategory,
    ToolDefinition,
    ToolManager,
    ToolNotConfiguredError,
)
from .version_resolver import (
    AmbiguousVersionError,
    ResolvedVersion,
    UnknownSeriesError,
    VersionResolver,
)

__version__ = "0.1.0-phase1"

__all__ = [
    "__version__",
    "setup_logger",
    "get_logger",
    "ConfigManager",
    "GameCatalogEntry",
    "TrustGrade",
    "GAME_CATALOG",
    "GAME_CATALOG_BY_KEY",
    "GamePathFinder",
    "PathLookupResult",
    "DetectionSource",
    "VersionResolver",
    "ResolvedVersion",
    "AmbiguousVersionError",
    "UnknownSeriesError",
    "ToolManager",
    "ToolDefinition",
    "ToolCategory",
    "ToolNotConfiguredError",
    "KNOWN_TOOLS",
    "TOOL_MAPPING",
]
