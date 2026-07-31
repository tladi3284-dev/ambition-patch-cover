import struct

from localizer import msg_viewer


def _build_synthetic_n11f(text: str, pointers: list) -> bytes:
    text_bytes = text.encode("cp932")
    pointer_table_offset = 8 + len(text_bytes) + len(msg_viewer.BOUNDARY_MARKER)
    body = text_bytes + msg_viewer.BOUNDARY_MARKER
    pointer_bytes = b"".join(struct.pack("<I", p) for p in pointers)
    header = b"N11F" + struct.pack("<I", pointer_table_offset)
    return header + body + pointer_bytes


def _build_synthetic_yabou(text1: str, header_values: list, offset_values: list, text2: str) -> bytes:
    text1_region_len = msg_viewer.YABOU_TEXT1_END + 1 - 8
    text1_bytes = text1.encode("cp932").ljust(text1_region_len, b"\x00")[:text1_region_len]

    decimal_values = header_values + offset_values
    decimal_region_len = msg_viewer.YABOU_DECIMAL_TABLE_END + 1 - msg_viewer.YABOU_DECIMAL_TABLE_START
    decimal_region = b"".join(f"{v:08d}".encode("ascii") for v in decimal_values)
    decimal_region = decimal_region.ljust(decimal_region_len, b"0")[:decimal_region_len]

    text2_bytes = text2.encode("cp932")

    data = bytearray(msg_viewer.YABOU_TEXT2_START + len(text2_bytes))
    data[0:4] = b"N11F"
    data[4:8] = struct.pack("<I", 0)
    data[8:8 + len(text1_bytes)] = text1_bytes
    data[msg_viewer.YABOU_BOUNDARY_START:msg_viewer.YABOU_BOUNDARY_END + 1] = msg_viewer.BOUNDARY_MARKER
    data[msg_viewer.YABOU_DECIMAL_TABLE_START:msg_viewer.YABOU_DECIMAL_TABLE_END + 1] = decimal_region
    data[msg_viewer.YABOU_TEXT2_START:] = text2_bytes
    return bytes(data)


def test_read_n11f_container_roundtrip(tmp_path):
    path = tmp_path / "sample.n11"
    path.write_bytes(_build_synthetic_n11f("こんにちは,MSG001", [0x1000, 0x1004, 0x1008]))

    container = msg_viewer.read_n11f_container(path)

    assert container.text_decoded == "こんにちは,MSG001"
    assert container.boundary_marker == msg_viewer.BOUNDARY_MARKER
    assert container.read_pointer_table_u32() == [0x1000, 0x1004, 0x1008]


def test_read_n11f_container_rejects_bad_magic(tmp_path):
    path = tmp_path / "bad.n11"
    path.write_bytes(b"XXXX" + b"\x00" * 8)
    try:
        msg_viewer.read_n11f_container(path)
        assert False, "expected NotAnN11FContainerError"
    except msg_viewer.NotAnN11FContainerError:
        pass


def test_read_n11f_container_rejects_misaligned_pointer_table(tmp_path):
    path = tmp_path / "misaligned.n11"
    data = _build_synthetic_n11f("hi", [1, 2])
    path.write_bytes(data + b"\x00")  # extra trailing byte breaks the %4 == 0 rule
    try:
        msg_viewer.read_n11f_container(path)
        assert False, "expected NotAnN11FContainerError"
    except msg_viewer.NotAnN11FContainerError:
        pass


def test_read_yabou_container(tmp_path):
    path = tmp_path / "yabou.n11"
    header_values = [308, 26292, 0, 0]
    offset_values = list(range(100, 100 + 307))
    path.write_bytes(_build_synthetic_yabou("dummy text region", header_values, offset_values, ",,Error test"))

    container = msg_viewer.read_yabou_container(path)

    assert container.header_values == header_values
    assert container.offset_values == offset_values
    assert container.text2_decoded == ",,Error test"
    assert container.boundary_marker == msg_viewer.BOUNDARY_MARKER


def test_find_msg_tag_candidates_finds_known_prefixes():
    text = "MSG001,bp1,din,dialogue text MSG002"
    candidates = msg_viewer.find_msg_tag_candidates(text)
    prefixes_found = {c["prefix"] for c in candidates}
    assert prefixes_found == {"MSG", "bp1", "din"}
    assert candidates == sorted(candidates, key=lambda c: c["char_offset"])
