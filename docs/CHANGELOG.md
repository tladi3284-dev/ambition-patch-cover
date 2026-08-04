# Handover Document Changelog

## NOBU11_REDUCED_SCOPE_DESIGN_REPORT_R2 — 2026-08-04
- Received a user-uploaded `.docx` (`nobu11______________________R2.docx`):
  a Revision-2 "reduced-scope" project design report
  (`DOCUMENT_ID: NOBU11_REDUCED_SCOPE_DESIGN_REPORT_20260805`) proposing to
  narrow all *future active work* from the exhaustive reverse-engineering
  track (MSG/pointer/control-code/font/EXE analysis) down to a minimal,
  batch-based, natural-Korean MSG-file translation workflow.
- Converted verbatim to Markdown (stdlib XML walk of `word/document.xml`,
  preserving headings/bullets/code blocks) and saved to
  `docs/NOBU11_REDUCED_SCOPE_DESIGN_REPORT_R2.md`, alongside
  `PROJECT_HANDOVER_v1.0.md`/`v2.0.md` since it is a project-wide scope/
  operation baseline rather than a `localizer_track`-specific technical spec.
- Per the document's own Ⅲ section, all prior project data/research is to be
  preserved, not discarded — nothing in this repository was deleted or
  rewritten as part of this ingestion.
- Flagged two gaps between the document's assumptions and current repo state
  (documented in full in the new file's "잉입 시 확인 사항" section):
  1. The document's Ⅵ/ⅩⅣ batch workflow assumes routine "MSG 파일 재구성"
     (MSG file rebuild/write-back), but `README.md` and
     `docs/localizer_track/CLAUDE_CODE_SPEC.md` §2.3/§3 currently list MSG
     write/rebuild as intentionally unimplemented — the N11F pointer-update
     rule needed for a safe rebuild is still unsolved.
  2. The document's `VERIFIED_SOURCE_ROOT`/`VERIFIED_SOURCE_MSG`/
     `VERIFIED_SOURCE_GRP` Google Drive verification claims are the
     document's own assertions; this ingestion did not independently access
     or confirm those folders.
- **Document-only ingestion.** No changes to `localizer/`, `tests/`,
  `README.md`, or `docs/localizer_track/CLAUDE_CODE_SPEC.md` — the reduced-
  scope batch workflow itself was not started.

## localizer_track/ACTUAL_GAME_READONLY_VALIDATION — 2026-07-31 (2nd)
- Instructed to run `localizer/` (commit `84f67ad`) read-only against the
  real game install at `GAME_ROOT: C:\Program Files (x86)\Steam\steamapps\
  common\Nobunaga11WPK`.
- That path is a Windows-local Steam path and does not exist in this
  remote Linux session; searched the repo, session uploads, and the whole
  filesystem for `*.n11`/`grp`/`steam`/`nobunaga` — found nothing but this
  session's own synthetic pytest fixtures. No real `msg/res/grp` files are
  reachable here.
- Did not fabricate scan/hash/parse results. Verified `git log` matches
  the instructed `BASE_COMMIT` and re-ran `pytest tests/ -v` (29/29 pass,
  synthetic fixtures only) as the one thing that could be honestly
  checked. Reproduced `validate-path --game-root <the given path>` to
  confirm it correctly reports `ok: false` rather than crashing.
- Wrote `docs/localizer_track/ACTUAL_GAME_READONLY_VALIDATION.md` with
  verdict `BLOCKED`, plus empty-header `artifacts/localizer/*.csv` and a
  `BLOCKED`-status `msg_parse_results.json` — no invented rows.
- SCEDA P0-P3 track untouched. Next step needs either running this
  pipeline on the user's own machine where `GAME_ROOT` is real, or
  uploading actual `msg/*.n11` / `res/*` files to this session.

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
