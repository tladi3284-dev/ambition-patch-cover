from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from PIL import Image
except ImportError:  # pragma: no cover - exercised only when Pillow is absent
    Image = None


@dataclass
class ImageMetadata:
    path: Path
    format: Optional[str]
    width: Optional[int]
    height: Optional[int]
    mode: Optional[str]
    readable: bool
    note: str


def inspect_image(path: Path) -> ImageMetadata:
    """
    Standard-format metadata only (PNG/BMP/etc via Pillow). Game-native
    containers like FONT.N11/FONT12.N11 are not standard image formats and
    are NOT parsed here — see CLAUDE_CODE_SPEC.md 2.3/4.4, unanalyzed.
    """
    path = Path(path)
    if Image is None:
        return ImageMetadata(path=path, format=None, width=None, height=None, mode=None,
                              readable=False, note="Pillow not installed")
    try:
        with Image.open(path) as img:
            return ImageMetadata(
                path=path, format=img.format, width=img.width, height=img.height,
                mode=img.mode, readable=True, note="parsed via Pillow",
            )
    except Exception as exc:
        return ImageMetadata(path=path, format=None, width=None, height=None, mode=None,
                              readable=False, note=f"not a standard image format or unreadable: {exc}")
