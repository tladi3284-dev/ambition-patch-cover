from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .models import SupportStatus

MAGIC_N11F = b"N11F"


class FileFormat(str, Enum):
    MSG_N11F_TEXT_PLUS_POINTER_TABLE = "MSG_N11F_TEXT_PLUS_POINTER_TABLE"
    MSG_YABOU_ASCII_DECIMAL = "MSG_YABOU_ASCII_DECIMAL"
    UNKNOWN_BINARY = "UNKNOWN_BINARY"


@dataclass
class ClassificationResult:
    path: Path
    file_format: FileFormat
    support_status: SupportStatus
    reason: str


def classify_file(path: Path) -> ClassificationResult:
    """
    Signature-based first pass only. A format is never marked SUPPORTED
    unless localizer has both a parser and a real-game-file verification
    note for it (see msg_viewer.py docstring for the N11F evidence).
    Everything else stays CONDITIONAL or UNKNOWN per
    CLAUDE_CODE_SPEC.md principle 6 (추측 금지) — this is fixed in place by
    test_no_format_is_ever_plain_supported.
    """
    path = Path(path)
    with path.open("rb") as f:
        header = f.read(8)

    if path.name.lower() == "yabou.n11":
        return ClassificationResult(
            path=path,
            file_format=FileFormat.MSG_YABOU_ASCII_DECIMAL,
            support_status=SupportStatus.CONDITIONAL,
            reason="yabou.n11 variant: read-only parser verified for text region 1 and the error-message "
                   "tail; pointer/offset-table semantics not fully closed (spec 2.3), so not SUPPORTED "
                   "for writes.",
        )

    if header[:4] == MAGIC_N11F:
        return ClassificationResult(
            path=path,
            file_format=FileFormat.MSG_N11F_TEXT_PLUS_POINTER_TABLE,
            support_status=SupportStatus.CONDITIONAL,
            reason="N11F magic matched; text region parses as CP932 with no encryption (measured on "
                   "69/69 sample files), but pointer-table-to-message mapping is unresolved, so writes "
                   "are not SUPPORTED yet.",
        )

    return ClassificationResult(
        path=path,
        file_format=FileFormat.UNKNOWN_BINARY,
        support_status=SupportStatus.UNKNOWN,
        reason="no known signature matched; format not analyzed.",
    )
