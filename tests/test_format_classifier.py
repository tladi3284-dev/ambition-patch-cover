from localizer import format_classifier
from localizer.models import SupportStatus


def test_n11f_magic_classified_conditional(tmp_path):
    path = tmp_path / "sample.n11"
    path.write_bytes(b"N11F" + (12).to_bytes(4, "little") + b"hi\x0a\x1f\x2c\x0a")
    result = format_classifier.classify_file(path)
    assert result.file_format == format_classifier.FileFormat.MSG_N11F_TEXT_PLUS_POINTER_TABLE
    assert result.support_status == SupportStatus.CONDITIONAL


def test_yabou_filename_classified_conditional(tmp_path):
    path = tmp_path / "yabou.n11"
    path.write_bytes(b"N11F" + b"\x00" * 4)
    result = format_classifier.classify_file(path)
    assert result.file_format == format_classifier.FileFormat.MSG_YABOU_ASCII_DECIMAL
    assert result.support_status == SupportStatus.CONDITIONAL


def test_unknown_signature_classified_unknown(tmp_path):
    path = tmp_path / "mystery.bin"
    path.write_bytes(b"\x00\x01\x02\x03random bytes")
    result = format_classifier.classify_file(path)
    assert result.file_format == format_classifier.FileFormat.UNKNOWN_BINARY
    assert result.support_status == SupportStatus.UNKNOWN


def test_no_format_is_ever_plain_supported(tmp_path):
    samples = [
        b"N11F" + (12).to_bytes(4, "little") + b"hi\x0a\x1f\x2c\x0a",
        b"\x00\x01\x02\x03",
    ]
    for i, data in enumerate(samples):
        path = tmp_path / f"f{i}.bin"
        path.write_bytes(data)
        result = format_classifier.classify_file(path)
        assert result.support_status != SupportStatus.SUPPORTED
