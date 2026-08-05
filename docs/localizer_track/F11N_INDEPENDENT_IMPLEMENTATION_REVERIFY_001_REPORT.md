# F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001 — Report

```yaml
TASK_ID: F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001
DATE: 2026-08-05
BASE_COMMIT: 1993b71
MODE: READ_ONLY
INPUT_FILES: 70 (same real msg/*.n11 set validated in
  ACTUAL_GAME_READONLY_VALIDATION_v2.md, unchanged)
```

## Scope compliance

Read-only throughout. No `msg` file was modified, no translation was
performed, no `grp`/FONT/EXE analysis was done, no repacking, no game
execution. Only actions taken: reading the existing 70-file local reference
mirror (`work/nobu11_workspace/source_reference/msg/`, itself read-only from
the prior task), writing a new standalone script, running it read-only, and
writing comparison JSON + these two markdown files.

## Phase A — Implementation separation

- Existing implementations in this repo: **one** —
  `localizer/msg_viewer.py` (`read_n11f_container`, `read_yabou_container`,
  `find_msg_tag_candidates`).
- No "Stage2" implementation, no other N11F/yabou parser, exists anywhere in
  this repository (checked via `grep -ril` across `*.py`/`*.md` for
  `stage2`/`Stage 2`/related terms — zero matches).
- New independent implementation written for this task:
  `scripts/independent_n11f_verifier.py`. Import check shows it imports
  nothing from `localizer` (only `json`, `sys`, `pathlib`). Uses manual
  `int.from_bytes`-style slicing in two classes (`IndependentN11FReader`,
  `IndependentYabouReader`), a different code shape from `msg_viewer.py`'s
  dataclass + `struct.unpack` approach.
- Shared dependency that does exist and must be disclosed: **the documented
  byte-offset facts themselves** (magic location, pointer-table-offset field,
  boundary marker bytes, yabou's fixed region offsets). Both implementations
  were written with knowledge of `msg_viewer.py`'s own docstring and
  `CLAUDE_CODE_SPEC.md` §2. This is independent *implementation*, not
  independent *discovery* — see the Decision doc for why that distinction
  matters for how this result should be weighted.

## Phase B — Comparison (same 70 input files, two implementations)

### Normal N11F variant (69 files)

Compared fields: `pointer_table_offset`, `pointer_count` (entry_count),
`boundary_ok`, `cp932_decode_ok`, and full `decoded_text` string equality
(not just length).

| field | CONSISTENT | DIFFERENT | UNKNOWN |
|---|---:|---:|---:|
| pointer_table_offset | 69 | 0 | 0 |
| pointer_count | 69 | 0 | 0 |
| boundary_ok | 69 | 0 | 0 |
| cp932_decode_ok | 69 | 0 | 0 |
| decoded_text (full string equality) | 69 | 0 | 0 |

Files with at least one `DIFFERENT` field: **0 / 69**.

Full per-file data:
`work/nobu11_workspace/reports/independent_reverify_comparison_normal.json`
(gitignored raw source files aside, this comparison JSON itself is committed).

### yabou.n11 variant (1 file)

| field | result |
|---|---|
| boundary_ok | CONSISTENT |
| header_values (`[308, 26292, 0, 0]`) | CONSISTENT |
| offset_value_count (307) | CONSISTENT |
| offset_values (full 307-entry array equality) | CONSISTENT |
| text1_length | CONSISTENT |
| text1_content_equal (full string) | CONSISTENT |
| text2_length | CONSISTENT |
| text2_content_equal (full string) | CONSISTENT |
| text2_starts_with_Error marker | CONSISTENT |

Full data:
`work/nobu11_workspace/reports/independent_reverify_comparison_yabou.json`.

## Phase C — Difference log

No differences occurred. Per the task's own rule (record `DIFFERENT` without
explaining it), there is nothing to log here — the log is empty by observed
result, not by omission. Total: **0 `DIFFERENT` entries across 70 files and
14 compared fields (5 fields × 69 normal files + 9 fields × 1 yabou file).**

## Phase D — Evidence classification

Using only the three permitted levels (`Observation`, `Reproduced
Observation`, `Cross-Validated Observation`; `CONFIRMED` not used anywhere in
this document):

| claim | prior level | level after this task |
|---|---|---|
| N11F magic/pointer-offset/boundary-marker/CP932-text layout holds on real files | Reproduced Observation (69/69 files, single implementation — `ACTUAL_GAME_READONLY_VALIDATION_v2.md`) | **Cross-Validated Observation** (69/69 files, two independent implementations agree) |
| yabou.n11 header values `[308, 26292, 0, 0]`, 307 offset entries, text2 `,,Error` prefix | Reproduced Observation (1/1 file, single implementation) | **Cross-Validated Observation** (1/1 file, two independent implementations agree) |
| Pointer-table-entry ↔ logical-message-span mapping | Unresolved | **Unchanged — still unresolved.** Not in scope, not attempted. |
| yabou header-value meaning; 307 vs 306 count mismatch cause | Unresolved | **Unchanged — still unresolved.** Not in scope, not attempted. |

Per the Decision doc's scope-limit note: "Cross-Validated" here means
validated against a second *implementation* of the same known layout, not
against a second *independent discovery* of the layout from raw bytes alone.

## Classification compliance

No new classification categories were introduced beyond what the task
specified (`CONSISTENT` / `DIFFERENT` / `UNKNOWN` for Phase C;
`Observation` / `Reproduced Observation` / `Cross-Validated Observation` for
Phase D). `localizer/format_classifier.py`'s own taxonomy
(`MSG_N11F_TEXT_PLUS_POINTER_TABLE` / `MSG_YABOU_ASCII_DECIMAL` /
`UNKNOWN_BINARY`, `CONDITIONAL` / `SUPPORTED` / `UNKNOWN`) was not touched or
reclassified by this task.

## Reporting compliance

This report and the accompanying Decision doc were checked for the
prohibited terms (`confirmed`, `solved`, `proved`, `final`, `complete`) —
none are used to characterize this task's results. `STATUS: PRELIMINARY` and
`VERIFICATION: REVERIFY_REQUIRED` are used as specified.

## Completion criteria

- [x] Independent-implementation status evaluated (Phase A: one prior
      implementation existed, none other; a new independent one was written
      for this task, with its shared-knowledge limitation disclosed).
- [x] Cross-implementation comparison completed (Phase B: 70/70 files, all
      compared fields, full-string/full-array equality where applicable, not
      just counts/lengths).
- [x] Shared-dependency status recorded (documented byte-offset facts are
      shared; no shared code — verified via import check).
- [x] Evidence level re-evaluated (Phase D table above).

## Expected status (matches task spec)

```yaml
STATUS: PRELIMINARY
VERIFICATION: REVERIFY_REQUIRED
EVIDENCE: INDEPENDENT_REPRODUCTION_COMPLETED_WITHIN_STATED_LIMITS
NOT_ATTEMPTED: pointer-tag correlation research, control-code catalog,
  blind independent structural discovery (as opposed to independent
  implementation of the known structure), grp/FONT analysis, translation,
  game execution.
```
