from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class PathValidationResult:
    game_root: Path
    exists: bool
    is_directory: bool
    msg_dir_found: bool
    res_dir_found: bool
    grp_dir_found: bool
    warnings: List[str]

    @property
    def ok(self) -> bool:
        return self.exists and self.is_directory


def validate_game_root(game_root: Path) -> PathValidationResult:
    """
    Read-only inspection only — never writes, never guesses which game
    version/edition is installed. Presence of msg/res/grp subfolders is
    reported as observed fact, not inferred from a version string.
    """
    game_root = Path(game_root)
    warnings: List[str] = []
    exists = game_root.exists()
    is_directory = game_root.is_dir() if exists else False

    msg_found = (game_root / "msg").is_dir()
    res_found = (game_root / "res").is_dir()
    grp_found = (game_root / "grp").is_dir()

    if not exists:
        warnings.append(f"game_root does not exist: {game_root}")
    elif not is_directory:
        warnings.append(f"game_root is not a directory: {game_root}")
    else:
        if not msg_found:
            warnings.append("msg/ subfolder not found")
        if not res_found:
            warnings.append("res/ subfolder not found")
        if not grp_found:
            warnings.append("grp/ subfolder not found")

    return PathValidationResult(
        game_root=game_root,
        exists=exists,
        is_directory=is_directory,
        msg_dir_found=msg_found,
        res_dir_found=res_found,
        grp_dir_found=grp_found,
        warnings=warnings,
    )
