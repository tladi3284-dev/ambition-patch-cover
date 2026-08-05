"""
Independent, standalone N11F/yabou reader for cross-validation against
localizer/msg_viewer.py, per TASK F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001.

Deliberately does NOT import anything from the `localizer` package. It is a
second, separately-written code path over the same documented byte layout
(magic bytes, pointer-table offset, boundary marker, CP932 text region;
yabou's fixed offset regions), using a different parsing style
(int.from_bytes + manual slicing in a class, vs. msg_viewer.py's dataclass +
struct.unpack functions) so that a coding bug specific to one implementation
(off-by-one slice, wrong endianness call, wrong codec name, etc.) would show
up as a mismatch here.

Honest scope limit (documented for Phase A of the reverify task): this is
independent *implementation*, not independent *discovery*. Both this script
and msg_viewer.py start from the same already-documented byte-offset
understanding (recorded in msg_viewer.py's own docstring and
CLAUDE_CODE_SPEC.md section 2). This script was not written by someone blind
to that documentation. It therefore cannot rule out a shared misunderstanding
of the format baked into that documentation itself — it can only catch bugs
introduced during implementation of a known layout. That distinction is
carried into the report's evidence classification.

Read-only: only ever opens files for reading. Never writes to any msg/*.n11
file, never touches grp/FONT/EXE, never runs the game.
"""
import json
import sys
from pathlib import Path

MAGIC = b"N11F"
BOUNDARY = b"\x0a\x1f\x2c\x0a"

YABOU_TEXT1_END = 9250
YABOU_BOUNDARY_START = 9251
YABOU_BOUNDARY_END = 9254
YABOU_TABLE_START = 9255
YABOU_TABLE_END = 11742
YABOU_ENTRY_WIDTH = 8
YABOU_ENTRY_COUNT = 311
YABOU_TEXT2_START = 11743


class IndependentN11FReader:
    """Manual byte-slicing reader, no struct module, no shared code with localizer/msg_viewer.py."""

    def __init__(self, raw: bytes):
        self.raw = raw

    def magic_ok(self) -> bool:
        return self.raw[0:4] == MAGIC

    def pointer_table_offset(self) -> int:
        b = self.raw[4:8]
        return b[0] | (b[1] << 8) | (b[2] << 16) | (b[3] << 24)

    def text_region(self, ptr_offset: int) -> bytes:
        return self.raw[8: ptr_offset - 4]

    def boundary_marker(self, ptr_offset: int) -> bytes:
        return self.raw[ptr_offset - 4: ptr_offset]

    def pointer_table(self, ptr_offset: int):
        tail = self.raw[ptr_offset:]
        count = len(tail) // 4
        values = []
        for i in range(count):
            chunk = tail[i * 4:(i + 1) * 4]
            values.append(chunk[0] | (chunk[1] << 8) | (chunk[2] << 16) | (chunk[3] << 24))
        return values


class IndependentYabouReader:
    def __init__(self, raw: bytes):
        self.raw = raw

    def text1(self) -> bytes:
        return self.raw[8: YABOU_TEXT1_END + 1]

    def boundary_marker(self) -> bytes:
        return self.raw[YABOU_BOUNDARY_START: YABOU_BOUNDARY_END + 1]

    def decimal_values(self):
        region = self.raw[YABOU_TABLE_START: YABOU_TABLE_END + 1]
        out = []
        for i in range(YABOU_ENTRY_COUNT):
            start = i * YABOU_ENTRY_WIDTH
            chunk = region[start: start + YABOU_ENTRY_WIDTH]
            if len(chunk) < YABOU_ENTRY_WIDTH:
                break
            digits = chunk.decode("ascii")
            out.append(int(digits))
        return out

    def text2(self) -> bytes:
        return self.raw[YABOU_TEXT2_START:]


def verify_normal_file(path: Path) -> dict:
    raw = path.read_bytes()
    reader = IndependentN11FReader(raw)
    result = {"file": path.name}
    if not reader.magic_ok():
        result["magic_ok"] = False
        return result
    result["magic_ok"] = True
    ptr_offset = reader.pointer_table_offset()
    result["pointer_table_offset"] = ptr_offset
    text_bytes = reader.text_region(ptr_offset)
    boundary = reader.boundary_marker(ptr_offset)
    result["boundary_ok"] = boundary == BOUNDARY
    try:
        decoded = text_bytes.decode("cp932")
        result["cp932_decode_ok"] = True
        result["decoded_text"] = decoded
        result["text_length"] = len(decoded)
    except UnicodeDecodeError:
        result["cp932_decode_ok"] = False
        result["decoded_text"] = None
        result["text_length"] = None
    pointers = reader.pointer_table(ptr_offset)
    result["pointer_count"] = len(pointers)
    return result


def verify_yabou_file(path: Path) -> dict:
    raw = path.read_bytes()
    reader = IndependentYabouReader(raw)
    result = {"file": path.name, "file_size": len(raw)}
    boundary = reader.boundary_marker()
    result["boundary_ok"] = boundary == BOUNDARY
    values = reader.decimal_values()
    result["header_values"] = values[:4]
    result["offset_value_count"] = len(values[4:])
    try:
        t1 = reader.text1().decode("cp932")
        result["text1_decode_ok"] = True
        result["text1_len"] = len(t1)
    except UnicodeDecodeError:
        result["text1_decode_ok"] = False
        result["text1_len"] = None
    try:
        t2 = reader.text2().decode("cp932")
        result["text2_decode_ok"] = True
        result["text2_len_if_decoded"] = len(t2)
        result["text2_starts_with_Error_marker"] = t2.startswith(",,Error")
    except UnicodeDecodeError:
        result["text2_decode_ok"] = False
        result["text2_len_if_decoded"] = None
        result["text2_starts_with_Error_marker"] = None
    return result


def main():
    msg_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("work/nobu11_workspace/source_reference/msg")
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("work/nobu11_workspace/reports/independent_verifier_results.json")

    files = sorted(msg_dir.glob("*.n11"))
    normal_results = []
    yabou_result = None
    for f in files:
        if f.name.lower() == "yabou.n11":
            yabou_result = verify_yabou_file(f)
        else:
            normal_results.append(verify_normal_file(f))

    out = {
        "total_files": len(files),
        "normal_n11f": normal_results,
        "yabou_variant": yabou_result,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"total_files": len(files), "normal_count": len(normal_results), "yabou_found": yabou_result is not None}, indent=2))


if __name__ == "__main__":
    main()
