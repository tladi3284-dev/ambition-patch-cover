from pathlib import Path


def is_within(path: Path, ancestor: Path) -> bool:
    try:
        Path(path).resolve().relative_to(Path(ancestor).resolve())
        return True
    except ValueError:
        return False
