# Handover Document Changelog

## localizer_track — 2026-07-31
- Received a separate spec document, `CLAUDE_CODE_SPEC.md`, describing a
  parallel technical track: a Python `localizer/` workbench targeting
  `msg/*.n11` (N11F pointer-table format) rather than the SCEDA
  scenario-title byte slots covered by the P0-P3 pipeline above. Saved to
  `docs/localizer_track/CLAUDE_CODE_SPEC.md`.
- The spec claimed "44 tests passing, 11 modules complete," but this
  repository had none of that code — only the spec markdown was uploaded.
  Per the project's own no-fabrication principle, this was flagged to the
  user rather than assumed. User chose to have the codebase built from
  scratch in this repo, based only on the spec's own structure/behavior
  description (no invented game-file evidence).
- Implemented `localizer/` (11 modules: `models`, `project_manager`,
  `path_validator`, `baseline_manager`, `workcopy_creator`,
  `format_classifier`, `file_scanner`, `msg_viewer`, `translation_schema`,
  `glossary_manager`, `res_inventory`, `image_research_viewer`, `cli`) and
  `tests/` (29 tests, synthetic fixtures only, no real game bytes), plus
  `requirements.txt` and `README.md`. All safety principles from the spec
  (original-read-only, workcopy separation, honest CONDITIONAL/UNKNOWN
  classification, translation status gate, deterministic-build hash
  verification) are enforced in code and covered by regression tests.
  `python3 -m pytest tests/ -v` — 29/29 passed.
- This track is independent of, and does not change, the SCEDA
  scenario-title P0-P3 pipeline's BLOCKED status described below — real
  `msg/res/grp` game files, `SCEDA`/`FONT.N11` parsers, and control-code
  catalogs are still not present in this repo.

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
