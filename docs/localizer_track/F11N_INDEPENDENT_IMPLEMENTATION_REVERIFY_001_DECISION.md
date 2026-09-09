# F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001 — Decision

```yaml
TASK_ID: F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001
DATE: 2026-08-05
BASE_COMMIT: 1993b71
MODE: READ_ONLY
STATUS: PRELIMINARY
VERIFICATION: REVERIFY_REQUIRED
EVIDENCE: CROSS_VALIDATED_WITHIN_STATED_LIMITS
```

## Objective (restated)

Check whether the N11F/yabou structure and decoding results already observed
against real `msg/*.n11` files (`docs/localizer_track/ACTUAL_GAME_READONLY_VALIDATION_v2.md`)
reproduce identically from a second, independently-written implementation —
not to discover new structure.

## Decision

**A second, independent implementation was written and run against all 70
real files. It reproduced every previously-recorded field identically —
0 `DIFFERENT`, 0 `UNKNOWN` across all compared fields on all 70 files.**

This raises the evidence level for the N11F/yabou byte-layout observations
from a single-implementation result to a cross-validated one, **within the
scope limit stated below**. It does not raise the confidence of anything
`localizer/msg_viewer.py`'s own docstring already marks unresolved (pointer↔
message-span mapping, control-code catalog, yabou header/count meaning) —
those remain untouched and unattempted by this task.

## Scope limit that must travel with this result (Phase A finding)

This repository has exactly one pre-existing N11F/yabou implementation:
`localizer/msg_viewer.py`. No "Stage2" implementation, or any other parser,
exists anywhere in this repo (`grep`-verified across `*.py`/`*.md`). There was
therefore no pre-existing second implementation to check for shared
code/tables/constants against — the second implementation had to be written
for this task (`scripts/independent_n11f_verifier.py`).

That new script:
- Imports nothing from the `localizer` package (verified: only `json`, `sys`,
  `pathlib` imported).
- Uses a different parsing style (a class doing manual `int.from_bytes`-style
  byte slicing, vs. `msg_viewer.py`'s dataclass + `struct.unpack`), so an
  implementation-specific bug (wrong slice bound, wrong endianness call,
  wrong codec string, off-by-one) would surface as a mismatch.

**But it is not independent of the documented understanding of the format.**
Both implementations start from the same already-published byte-offset
facts (magic at 0–3, pointer-table-offset at 4–7, boundary marker
`b"\x0a\x1f\x2c\x0a"`, yabou's fixed offsets 9250/9251/9255/11742/11743,
etc.), recorded in `msg_viewer.py`'s own docstring and
`docs/localizer_track/CLAUDE_CODE_SPEC.md` §2. This reverify task therefore
tests **"does re-implementing the known layout from scratch reproduce
byte-identical results"** (catches coding bugs), not **"does a party blind to
the existing documentation independently arrive at the same structural
conclusion"** (which would require a separate blind-reimplementation
protocol this task did not run). Calling this result `CONFIRMED` or `PROVED`
would overstate it — per the task's own reporting rules, neither term is
used anywhere in this decision or the accompanying report.

## Status conclusion

`STATUS: PRELIMINARY`, `VERIFICATION: REVERIFY_REQUIRED` stays exactly as the
task spec's "Expected Status" anticipated — this result strengthens the
evidence for the *already-documented* structure, it does not close any of the
unresolved items in `CLAUDE_CODE_SPEC.md` §2.3, and it does not by itself
justify moving past `CONDITIONAL` support status for any file format.

Full comparison data and per-field results: see
`F11N_INDEPENDENT_IMPLEMENTATION_REVERIFY_001_REPORT.md` in this same
directory.
