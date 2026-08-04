# 실제 게임 파일 읽기 전용 검증 v2 — 결과: 실측 완료 (msg 전용, 최소 범위)

> **본 문서는 `ACTUAL_GAME_READONLY_VALIDATION.md`(v1, 판정 `BLOCKED`)를
> 대체한다.** v1은 역사적 기록으로 그대로 보존한다. v1의 `BLOCKED` 판정은
> 로컬 Windows Steam 경로(`C:\...`)가 이 원격 Linux 세션에서 접근 불가능하다는
> 것이었다 — 이번 검증은 그것과 다른 채널인 **Google Drive API 커넥터**로
> `docs/NOBU11_REDUCED_SCOPE_DESIGN_REPORT_R2.md`의 `VERIFIED_SOURCE_ROOT`를
> 실제로 열어본 결과다.

- 실행일: 2026-08-04
- 기준 커밋: `f8e6b58`
- 작업 모드: READ_ONLY (원본 Google Drive 파일에 쓰기 없음)
- 데이터 출처: Google Drive `VERIFIED_SOURCE_MSG` 폴더
  (`https://drive.google.com/drive/folders/1Q-MBBpyyZGmI92ULiFuOi5PzAREPfBST`),
  소유자 `tladi3284@gmail.com`
- 판정: **실측 완료 — `msg/*.n11` 70개 전량, 다른 폴더는 이번 범위 밖**

## 확인 절차

1. **Google Drive 접근성 확인** — 이번에 처음 시도. `mcp__Google_Drive__search_files`로
   `parentId = '1dYkAIGK_kpqofm_I3Dz44pX_BQTG7sQO'`(`SOURCE_GAME_ROOT`)를 조회한
   결과, R2 설계 보고서가 기술한 구조(`BGM`, `Cursor`, `HTML`, `MOVIE`, `SE`,
   `grp`, `map`, `msg`, `scenario`, `trial`, `Nobunaga11WPK.exe`,
   `Nobunaga11WPK_Launcher.exe`, `Nobunaga11WPK.pdf`, `graphres.bin` 등)와
   정확히 일치함을 확인했다. `res/` 폴더는 이 목록에 없다 — v1의 "res 없음"
   가정과 달리, 이번 실측으로 Drive 원본 자체에 `res/` 폴더가 없다는 것을
   직접 확인했다(추측 아님).
2. **`msg/*.n11` 70개 파일 다운로드 및 크기 검증** — 완료.
   - `parentId = '1Q-MBBpyyZGmI92ULiFuOi5PzAREPfBST'`(`msg` 폴더) 조회 결과
     정확히 70개의 `.n11` 파일이 확인됨 (기존 문서들이 일관되게 언급해 온
     "전체 70개 MSG 파일"과 일치).
   - 각 파일을 `mcp__Google_Drive__download_file_content`로 원본 그대로
     내려받아 `work/nobu11_workspace/source_reference/msg/`에 저장.
   - 다운로드 직후 파일별 디스크 크기를 Drive 메타데이터의 `size` 값과 다시
     대조 — **70/70 정확히 일치, 누락/추가 파일 0건** (독립적으로 재확인함,
     아래 재현 로그 참고).
3. **SHA-256 해시 기록** — `localizer.baseline_manager.build_manifest()`로
   70개 파일 전체 해시 계산, `artifacts/localizer/original_sha256.csv`에 기록.
4. **`project-init` → `validate-path` → `scan` → `make-workcopy`** — 전부
   기존 CLI(`localizer/cli.py`)로, 코드 수정 없이 실행. 아래 재현 로그 참고.
5. **`msg-inspect` 실측 검증** — `localizer/msg_viewer.py`의
   `read_n11f_container`(69개 일반 계열)와 `read_yabou_container`(`yabou.n11`
   1개)를 실제 파일에 직접 실행.

### 재현 로그 (실제 명령 출력)

```
$ python -m localizer.cli project-init \
    --root work/nobu11_workspace \
    --original-source work/nobu11_workspace/source_reference \
    --workcopy work/nobu11_workspace/working \
    --backup work/nobu11_workspace/backup \
    --output work/nobu11_workspace/reports
{
  "original_source_path": "/home/user/taishi/work/nobu11_workspace/source_reference",
  "workcopy_path": "work/nobu11_workspace/working",
  "backup_path": "work/nobu11_workspace/backup",
  "output_path": "work/nobu11_workspace/reports"
}

$ python -m localizer.cli validate-path --game-root work/nobu11_workspace/source_reference
{
  "game_root": "work/nobu11_workspace/source_reference",
  "ok": true,
  "msg_dir_found": true,
  "res_dir_found": false,
  "grp_dir_found": false,
  "warnings": [
    "res/ subfolder not found",
    "grp/ subfolder not found"
  ]
}

$ python -m localizer.cli scan --root work/nobu11_workspace
{
  "file_count": 70,
  "json": "work/nobu11_workspace/reports/scan_report.json",
  "csv": "work/nobu11_workspace/reports/scan_report.csv"
}
# 분류 집계: MSG_N11F_TEXT_PLUS_POINTER_TABLE=69, MSG_YABOU_ASCII_DECIMAL=1
# support_status: 전부 CONDITIONAL (SUPPORTED 0건 — 설계 원칙대로)

$ python -m localizer.cli make-workcopy --root work/nobu11_workspace --allow-existing
{
  "workcopy_path": "work/nobu11_workspace/working"
}
# workcopy_creator의 복사-후-해시 재검증 통과 (WorkcopyHashMismatchError 없음)
```

`grp_dir_found: false`/`res_dir_found: false`는 "접근 불가"가 아니라 **의도적
범위 제한**이다 — `grp/`는 Drive에 실제로 존재함을 1단계에서 이미 확인했지만,
이번 검증은 R2 설계 보고서의 초기 활성 범위(`msg/*.n11`)만 대상으로 했으므로
다운로드하지 않았다. `res/`는 Drive 원본 자체에 없음을 1단계에서 확인했다.

### `msg_viewer.py` 실측 결과 (69개 일반 계열)

```python
>>> from localizer import msg_viewer
>>> [msg_viewer.read_n11f_container(f) for f in msg_dir.glob("*.n11") if f.name != "yabou.n11"]
# 69/69 파일 모두:
#   - N11F 매직 확인 (아니면 NotAnN11FContainerError 발생 — 0건 발생)
#   - boundary_marker == b"\x0a\x1f\x2c\x0a"  → 69/69 일치
#   - text_bytes.decode("cp932") 성공        → 69/69 성공, UnicodeDecodeError 0건
#   - 예외/파싱 실패                          → 0건
```

전체 결과는 `artifacts/localizer/msg_parse_results.json`의
`results.normal_n11f` 배열(69개 항목, 파일별 `boundary_ok`/`pointer_count`/
`cp932_decode_ok`/`tag_candidate_count`)에 기록되어 있다.

### `yabou.n11` 실측 결과

```
$ python -c "... msg_viewer.read_yabou_container(Path('.../yabou.n11')) ..."
{
  "file_size": 20274,
  "boundary_ok": true,
  "header_values": [308, 26292, 0, 0],
  "offset_value_count": 307,
  "text1_decode_ok": true,
  "text1_len": 9243,
  "text2_decode_ok": true,
  "text2_starts_with_Error_marker": true,
  "text2_len_if_decoded": 4385
}
```

`msg_viewer.py`의 docstring이 문서화해 온 "관찰값: 308, 26292, 0, 0"과
"307개 오프셋 값"과 "`,,Error`로 시작"이 실제 파일에서 **정확히 재현됨** —
이 저장소에서 처음으로 독립 재확인된 것이다. `header_values`의 의미와
`307 vs 306` 불일치 원인은 여전히 미상으로 남아 있다(추측 안 함, §2.3 그대로
유지).

## 검증 요약

```yaml
ORIGINAL_HASH_CHANGES: 0        # Google Drive 원본 파일에 쓰기 안 함
WORKCOPY_HASH_MISMATCHES: 0     # make-workcopy 사후 해시 재검증 통과
UNHANDLED_EXCEPTIONS: 0
ACTUAL_FILES_TESTED: 70
PARSE_RESULTS_BY_FORMAT:
  MSG_N11F_TEXT_PLUS_POINTER_TABLE: 69/69 parsed, 69/69 boundary marker match, 69/69 CP932 decode OK
  MSG_YABOU_ASCII_DECIMAL: 1/1 parsed, header/offset/text1/text2 values match documented claims exactly
CONDITIONAL_FILES: 70          # 전부 CONDITIONAL, SUPPORTED 0건
UNSUPPORTED_FILES: 0
UNKNOWN_BINARY_FILES: 0
```

## 이번 검증이 확인하지 "않은" 것 (범위 밖, 추측 금지)

- `MSGn` 태그와 포인터 테이블 항목의 대응 관계 (CLAUDE_CODE_SPEC.md §2.3의
  미해결 항목 — 이번 검증은 이 상관관계를 시도하지 않았다. 이는 사용자가
  이번 패스의 범위에서 명시적으로 제외했다.)
- 제어 코드 카탈로그.
- `grp/FONT.N11`, `grp/FONT12.N11`, `res/`(Drive에 없음 확인됨), `SCEDA`/
  `DBSCEDA` — 전부 미다운로드/미분석.
- 포인터 갱신 규칙(재구축/쓰기 경로) — 여전히 미구현, 미시도.
- 실제 게임 실행/화면 표시 검증 — 이 세션은 Windows 게임 실행 환경이 아니므로
  수행 불가.

## 금지 사항 준수 확인

- Google Drive 원본 수정: 안 함 — 모든 접근은 `search_files`/`download_file_content`
  (읽기 전용 API)뿐.
- 로컬 게임 설치 폴더에 쓰기: 해당 없음 — 이 세션에는 로컬 게임 설치가 없음.
- 번역 삽입 / 포인터 재계산 / 파일 재구축 / FONT·res 쓰기 / 게임 실행: 안 함.
- 지원 상태를 근거 없이 `SUPPORTED`로 변경: 안 함 — 70/70 전부 `CONDITIONAL`로
  분류됨, `format_classifier.py` 원본 코드 수정 없음.
- 기존 SCEDA 트랙 상태 변경: 안 함.
- `MSGn`-태그/포인터 상관관계 연구, 번역 배치 작업: 이번 범위에서 명시적으로
  제외 — 수행 안 함.

## 산출물

- `work/nobu11_workspace/source_reference/msg/*.n11` — Drive에서 내려받은
  읽기 전용 참조 사본 70개 (원본은 Drive에 그대로 있음, 이 사본을 직접 수정한
  적 없음).
- `work/nobu11_workspace/reports/original_sha256_manifest.json` — 70개 파일
  SHA-256 매니페스트.
- `work/nobu11_workspace/reports/scan_report.{json,csv}` — CLI `scan` 산출물.
- `work/nobu11_workspace/working/` — `make-workcopy`로 생성된 작업 사본
  (해시 검증 통과).
- `artifacts/localizer/original_sha256.csv` — 70 rows, 실제 해시.
- `artifacts/localizer/file_inventory.csv` — 70 rows, 실제 크기/분류.
- `artifacts/localizer/format_classification.csv` — 70 rows, 실제 분류 결과.
- `artifacts/localizer/msg_parse_results.json` — `status: VALIDATED_AGAINST_REAL_FILES`,
  `files_tested: 70`, 파일별 파싱 결과.
- `artifacts/localizer/res_inventory.csv` — 여전히 헤더만, 0 rows
  (`res/`가 Drive 원본에 실제로 없음을 이번에 확인했으므로 그대로 유지 — v1의
  "확인 불가"와 달리 이번엔 "확인 결과 없음").

## 다음 담당자를 위한 참고

- 이번 검증으로 `msg_viewer.py`의 N11F/yabou 파서가 실제 게임 데이터에 대해
  구조적으로 정확함이 처음 독립 확인되었다. `localizer/msg_viewer.py` 코드
  자체는 수정하지 않았다(버그가 발견되지 않았으므로).
- `MSGn` 태그 ↔ 포인터 테이블 상관관계 연구(CLAUDE_CODE_SPEC.md §4.1)는
  이제 실제 데이터가 로컬에 있으므로 시도 가능한 상태이지만, 이번 패스의
  범위에는 포함되지 않았다 — 별도 작업으로 남겨둔다.
- R2 설계 보고서(Ⅵ 최소한도 작업 원칙)의 실제 번역 배치 작업도 이번 범위
  밖이다.

## 최종 보고

```yaml
COMMIT: f8e6b58
FILES_SCANNED: 70
MSG_FILES: 70
RES_FILES: 0 (res/ confirmed absent from Drive source root, not just unmirrored)
PARSE_PASS: 70/70 (69 normal N11F + 1 yabou variant)
CONDITIONAL: 70
UNSUPPORTED: 0
UNKNOWN_BINARY: 0
ORIGINAL_HASH_CHANGES: 0
WORKCOPY_HASH_MISMATCHES: 0
NEW_TESTS: 0 (synthetic-fixture suite untouched, still 29/29 pass)
TEST_RESULT: 29/29 PASS (pre-existing synthetic-fixture suite, unrelated to this validation)
DATA_SOURCE: Google Drive API (VERIFIED_SOURCE_MSG), not local filesystem —
  distinct access channel from the v1 report's Windows-local-path attempt.
NOT_ATTEMPTED_THIS_PASS: MSGn-tag/pointer-table correlation research,
  control-code catalog, grp/FONT analysis, translation batch work, real
  game execution (no Windows environment available here).
NEXT_GATE: Real-data foundation is now in place under
  work/nobu11_workspace/source_reference/msg/. Follow-up work (correlation
  research, translation batches per the R2 report) can build on this without
  re-downloading, but each remains a separate, explicitly-scoped task.
```
