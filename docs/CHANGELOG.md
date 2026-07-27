# Handover Document Changelog

## v2.0 — 2026-07-27
- Superseded v1.0 with the consolidated handover ("통합 프로젝트 인수인계서").
- No new actual artifacts (P0-P2 JSON/reports, `hangul_code_map.json`, real
  encoder, pristine game files) were provided alongside v2.0 — it is a
  document-only update.
- Substantive content changes folded into this repo:
  - Expanded 21-byte slot-overflow risk list from 1 title to 5 titles
    (SCENARIO_TITLE_002, 003, 005, 006, 007) — see
    `work/p3_93cf11f5-eaa9-4743-af28-cd957b296834/reports/p3_unresolved_items.md`.
  - Added `capture_ocr_helper.py` reference hash (tool itself still absent
    from this repo).
  - Formalized Fail-Closed principle and `CODE_MAP_MODIFICATION: PROHIBITED`.
  - Named `BLOCKED_P2_EVIDENCE` as the specific status for P2-evidence gaps.
- **Overall Stage P3 verdict unchanged: BLOCKED.** The repository still lacks
  every input required for real byte/glyph validation.

## v1.0 — 2026-07-27
- Initial handover document ingested into a fresh Claude Code session.
- Repository (`tladi3284-dev/taishi`) found to have zero commits and none of
  the referenced P0-P2 artifacts.
- Produced `work/p3_93cf11f5-eaa9-4743-af28-cd957b296834/` gap analysis:
  P2 gap report, reference-only character list, BLOCKED translation ledger,
  safety report. See `docs/PROJECT_HANDOVER_v1.0.md` (superseded, kept for
  history).
