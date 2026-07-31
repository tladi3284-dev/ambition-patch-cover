"""
N11F msg container parser.

Structure measured directly against real game files under msg/*.n11
(71 files extracted from grp.7z), 2026-07-31.

Normal variant (69/69 files) — MSG_N11F_TEXT_PLUS_POINTER_TABLE:
  offset 0..3      magic b"N11F"
  offset 4..7      LE uint32 pointer_table_offset (T), absolute file offset
  offset 8..T-1    CP932 plaintext (verified: no XOR/encryption, 69/69 decode)
  offset T-4..T-1  fixed boundary marker b"\\x0a\\x1f\\x2c\\x0a" (69/69 files)
  offset T..EOF    LE uint32 pointer table; (EOF-T) % 4 == 0 holds for all 69

yabou.n11 variant (1 file) — MSG_YABOU_ASCII_DECIMAL:
  offset 8..9250       text region 1 (same CP932/tag shape as normal variant)
  offset 9251..9254    same fixed boundary marker
  offset 9255..11742   311 x 8-digit ASCII decimal numbers
                        - first 4 values: header-like, meaning unknown
                        - remaining 307: byte offsets into text region 1
  offset 11743..EOF    second text block, no own header, starts with
                        ",,Error", decodes 100% as CP932 (error strings)

UNRESOLVED — do not guess past this; see CLAUDE_CODE_SPEC.md 2.3:
  - exact pointer-table-entry <-> logical-message-span mapping
  - which comma-separated tokens are control codes vs dialogue text
  - yabou.n11 header 4 values; 307 vs 306 count mismatch
  - whether yabou.n11's second text block has its own offset table
  - pointer update rule on rebuild (write path intentionally unimplemented)
"""
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

MAGIC = b"N11F"
BOUNDARY_MARKER = b"\x0a\x1f\x2c\x0a"

YABOU_TEXT1_END = 9250
YABOU_BOUNDARY_START = 9251
YABOU_BOUNDARY_END = 9254
YABOU_DECIMAL_TABLE_START = 9255
YABOU_DECIMAL_TABLE_END = 11742
YABOU_DECIMAL_ENTRY_WIDTH = 8
YABOU_DECIMAL_ENTRY_COUNT = 311
YABOU_TEXT2_START = 11743


class NotAnN11FContainerError(Exception):
    pass


@dataclass
class N11FContainer:
    path: Path
    pointer_table_offset: int
    text_bytes: bytes
    boundary_marker: bytes
    pointer_table_bytes: bytes

    @property
    def text_decoded(self) -> str:
        return self.text_bytes.decode("cp932")

    def read_pointer_table_u32(self) -> List[int]:
        count = len(self.pointer_table_bytes) // 4
        return list(struct.unpack(f"<{count}I", self.pointer_table_bytes[: count * 4]))


def read_n11f_container(path: Path) -> N11FContainer:
    path = Path(path)
    data = path.read_bytes()
    if data[:4] != MAGIC:
        raise NotAnN11FContainerError(f"{path}: missing N11F magic")

    pointer_table_offset = struct.unpack("<I", data[4:8])[0]
    if pointer_table_offset > len(data) or pointer_table_offset < 8:
        raise NotAnN11FContainerError(
            f"{path}: pointer_table_offset {pointer_table_offset} out of range for file size {len(data)}"
        )

    text_bytes = data[8:pointer_table_offset - 4]
    boundary_marker = data[pointer_table_offset - 4:pointer_table_offset]
    pointer_table_bytes = data[pointer_table_offset:]

    if len(pointer_table_bytes) % 4 != 0:
        raise NotAnN11FContainerError(
            f"{path}: pointer table length {len(pointer_table_bytes)} is not a multiple of 4"
        )

    return N11FContainer(
        path=path,
        pointer_table_offset=pointer_table_offset,
        text_bytes=text_bytes,
        boundary_marker=boundary_marker,
        pointer_table_bytes=pointer_table_bytes,
    )


@dataclass
class YabouContainer:
    path: Path
    text1_bytes: bytes
    boundary_marker: bytes
    header_values: List[int]
    offset_values: List[int]
    text2_bytes: bytes

    @property
    def text1_decoded(self) -> str:
        return self.text1_bytes.decode("cp932")

    @property
    def text2_decoded(self) -> str:
        return self.text2_bytes.decode("cp932")


def read_yabou_container(path: Path) -> YabouContainer:
    path = Path(path)
    data = path.read_bytes()
    if data[:4] != MAGIC:
        raise NotAnN11FContainerError(f"{path}: missing N11F magic")

    text1_bytes = data[8:YABOU_TEXT1_END + 1]
    boundary_marker = data[YABOU_BOUNDARY_START:YABOU_BOUNDARY_END + 1]
    decimal_region = data[YABOU_DECIMAL_TABLE_START:YABOU_DECIMAL_TABLE_END + 1]
    text2_bytes = data[YABOU_TEXT2_START:]

    values = []
    for i in range(YABOU_DECIMAL_ENTRY_COUNT):
        start = i * YABOU_DECIMAL_ENTRY_WIDTH
        chunk = decimal_region[start:start + YABOU_DECIMAL_ENTRY_WIDTH]
        if len(chunk) < YABOU_DECIMAL_ENTRY_WIDTH:
            break
        values.append(int(chunk.decode("ascii")))

    header_values = values[:4]
    offset_values = values[4:]

    return YabouContainer(
        path=path,
        text1_bytes=text1_bytes,
        boundary_marker=boundary_marker,
        header_values=header_values,
        offset_values=offset_values,
        text2_bytes=text2_bytes,
    )


def find_msg_tag_candidates(text: str, tag_prefixes: Optional[List[str]] = None) -> List[dict]:
    """
    Observation helper for the experiment in CLAUDE_CODE_SPEC.md 4.1 — NOT a
    settled parser. Returns character offsets of substrings that look like
    known tag-style tokens (MSG/bp1/din, per spec 4.2), for a human or an
    experiment script to compare against the pointer table. Does not claim a
    resolved tag<->pointer mapping.
    """
    if tag_prefixes is None:
        tag_prefixes = ["MSG", "bp1", "din"]

    candidates = []
    for prefix in tag_prefixes:
        start = 0
        while True:
            idx = text.find(prefix, start)
            if idx == -1:
                break
            candidates.append({"prefix": prefix, "char_offset": idx})
            start = idx + len(prefix)
    candidates.sort(key=lambda c: c["char_offset"])
    return candidates
