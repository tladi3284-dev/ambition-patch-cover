import pytest

from localizer.models import TranslationStatus
from localizer.translation_schema import (
    ControlCodeLossError,
    InvalidStatusTransitionError,
    TranslationCorpus,
)


def test_add_entry_starts_not_translated():
    corpus = TranslationCorpus()
    entry = corpus.add_entry("T001", "こんにちは")
    assert entry.status == TranslationStatus.NOT_TRANSLATED


def test_status_cannot_skip_ahead():
    corpus = TranslationCorpus()
    corpus.add_entry("T001", "こんにちは")
    with pytest.raises(InvalidStatusTransitionError):
        corpus.advance_status("T001", TranslationStatus.APPROVED)


def test_status_cannot_go_backward():
    corpus = TranslationCorpus()
    corpus.add_entry("T001", "こんにちは")
    corpus.advance_status("T001", TranslationStatus.DRAFT)
    corpus.advance_status("T001", TranslationStatus.REVIEW_REQUIRED)
    with pytest.raises(InvalidStatusTransitionError):
        corpus.advance_status("T001", TranslationStatus.DRAFT)


def test_approve_rejects_control_code_loss():
    corpus = TranslationCorpus()
    corpus.add_entry("T001", "こんにちは{PLAYER}さん")
    corpus.set_translation("T001", "안녕하세요 님")
    for status in [TranslationStatus.DRAFT, TranslationStatus.REVIEW_REQUIRED,
                   TranslationStatus.HISTORY_REVIEWED, TranslationStatus.UI_REVIEWED]:
        corpus.advance_status("T001", status)
    with pytest.raises(ControlCodeLossError):
        corpus.advance_status("T001", TranslationStatus.APPROVED)


def test_approve_succeeds_when_control_codes_preserved():
    corpus = TranslationCorpus()
    corpus.add_entry("T001", "こんにちは{PLAYER}さん")
    corpus.set_translation("T001", "안녕하세요 {PLAYER}님")
    for status in [TranslationStatus.DRAFT, TranslationStatus.REVIEW_REQUIRED,
                   TranslationStatus.HISTORY_REVIEWED, TranslationStatus.UI_REVIEWED,
                   TranslationStatus.APPROVED]:
        corpus.advance_status("T001", status)
    assert corpus.entries["T001"].status == TranslationStatus.APPROVED
    assert "T001" in corpus.approved_entries()


def test_save_and_load_roundtrip(tmp_path):
    corpus = TranslationCorpus()
    corpus.add_entry("T001", "こんにちは")
    path = tmp_path / "corpus.json"
    corpus.save(path)

    loaded = TranslationCorpus.load(path)
    assert loaded.entries["T001"].source_japanese == "こんにちは"


def test_load_missing_file_returns_empty_corpus(tmp_path):
    loaded = TranslationCorpus.load(tmp_path / "does_not_exist.json")
    assert loaded.entries == {}
