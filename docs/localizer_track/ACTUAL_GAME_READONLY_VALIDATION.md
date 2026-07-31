# 실제 게임 파일 읽기 전용 검증 — 결과: BLOCKED

- 실행일: 2026-07-31
- 기준 커밋: `84f67ad`
- 작업 모드: READ_ONLY
- 지시된 `GAME_ROOT`: `C:\Program Files (x86)\Steam\steamapps\common\Nobunaga11WPK`
- 판정: **BLOCKED — 지시된 `GAME_ROOT`가 이 세션에서 접근 불가능함**

## 확인 절차

1. **저장소 코드·테스트 확인** — 완료.
   - `git log --oneline -3` → `84f67ad`가 현재 HEAD, 지시된 `BASE_COMMIT`과 일치.
   - `python3 -m pytest tests/ -v` → 29/29 PASS (전부 합성 픽스처 기반, 실제
     게임 파일 사용 안 함).
2. **`GAME_ROOT` 접근 시도** — 실패.
   - `ls -la 'C:\Program Files (x86)\Steam\steamapps\common\Nobunaga11WPK'` →
     `No such file or directory`.
   - 이 세션은 사용자의 Windows 로컬 머신이 아니라 격리된 원격 Linux 컨테이너다.
     Windows 드라이브 문자 경로(`C:\...`)는 애초에 이 파일시스템에 존재할 수
     없는 경로다.
   - 저장소 전체(`/home/user/taishi`), 업로드 폴더(`/root/.claude/uploads/...`),
     루트 파일시스템을 `*.n11`, `*grp*`, `*nobunaga*`, `*steam*` 패턴으로
     검색했으나 합성 테스트 픽스처(`/tmp/pytest-of-root/.../*.n11`) 외에는
     아무 실제 게임 데이터도 발견되지 않았다.
   - 업로드된 파일은 `CLAUDE_CODE_SPEC.md` 명세서 하나뿐이며, `msg/*.n11`,
     `res/*`, `grp.7z` 등 실제 바이너리는 첨부되지 않았다.
3. **3~8단계(작업 사본 생성, CLI 스캔/분류/파싱, res 조사, 실측/합성 구분)**
   — 실제 입력 파일이 없으므로 수행 불가. 입력 없이 이 단계들을 실행하면
   `localizer.path_validator.validate_game_root()`가 `ok: false`를 반환하고
   그 이후 모든 명령이 `FileNotFoundError`로 실패하는 것이 코드의 정상 동작이다
   (아래 재현 로그 참고). 이를 억지로 통과시키거나 가짜 해시/분류 결과를
   생성하는 것은 프로젝트 자체의 추측 금지·Fail-Closed 원칙 위반이므로 하지
   않았다.

### 재현 로그 (합성 부재 경로로 실제 동작 확인)

```
$ python3 -m localizer.cli validate-path --game-root 'C:\Program Files (x86)\Steam\steamapps\common\Nobunaga11WPK'
{
  "game_root": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Nobunaga11WPK",
  "ok": false,
  "msg_dir_found": false,
  "res_dir_found": false,
  "grp_dir_found": false,
  "warnings": [
    "game_root does not exist: C:\\Program Files (x86)\\Steam\\steamapps\\common\\Nobunaga11WPK"
  ]
}
```

## 검증 요약

```yaml
ORIGINAL_HASH_CHANGES: 0        # 원본에 접근한 적이 없으므로 자명하게 0
WORKCOPY_HASH_MISMATCHES: N/A   # 작업 사본을 만들지 않았음 (원본 없음)
UNHANDLED_EXCEPTIONS: 0         # validate-path는 위 로그처럼 정상적으로 ok:false 반환
ACTUAL_FILES_TESTED: 0
PARSE_RESULTS_BY_FORMAT: N/A (실제 msg/*.n11 없음)
CONDITIONAL_FILES: N/A
UNSUPPORTED_FILES: N/A
```

## 금지 사항 준수 확인

- Steam 원본 수정: 안 함 (애초에 접근 자체가 불가능했음).
- 번역 삽입 / 포인터 재계산 / 파일 재구축 / FONT·res 쓰기 / 게임 실행: 안 함.
- 지원 상태를 근거 없이 `SUPPORTED`로 변경: 안 함 — 실제 파일이 없으므로
  `format_classifier`를 실행할 대상 자체가 없었음.
- 기존 SCEDA 트랙 상태 변경: 안 함 — `work/p3_93cf11f5-eaa9-4743-af28-cd957b296834/`
  이하 파일 무변경.

## 산출물 (내용은 모두 "0건/빈 결과", 가짜 데이터 없음)

- `artifacts/localizer/file_inventory.csv` — 헤더만, 0 rows
- `artifacts/localizer/original_sha256.csv` — 헤더만, 0 rows
- `artifacts/localizer/format_classification.csv` — 헤더만, 0 rows
- `artifacts/localizer/msg_parse_results.json` — `status: BLOCKED`, `files_tested: 0`
- `artifacts/localizer/res_inventory.csv` — 헤더만, 0 rows

## 다음 담당자를 위한 필요 조치

이 작업을 실제로 수행하려면 다음 중 하나가 필요하다:

1. **로컬 실행** — 사용자의 Windows 머신(Steam 설치 경로에 실제 접근 가능한
   환경)에서 직접 `python -m localizer.cli` 파이프라인을 실행한다. 이 저장소의
   코드는 그대로 사용 가능하다 (`pip install -r requirements.txt` 후 커밋
   `84f67ad` 기준).
2. **파일 업로드** — `msg/*.n11`, `res/*` 실제 파일(또는 `grp.7z` 아카이브)을
   이 세션에 업로드하면, 그 경로를 `--original-source`로 지정해 이어서
   `project-init` → `validate-path` → `scan` → `make-workcopy` →
   `msg-inspect` 파이프라인을 실행할 수 있다.

둘 중 하나가 충족되기 전까지 이 검증은 `BLOCKED` 상태로 유지된다.

## 최종 보고

```yaml
COMMIT: 84f67ad
FILES_SCANNED: 0
MSG_FILES: 0
RES_FILES: 0
PARSE_PASS: 0
CONDITIONAL: 0
UNSUPPORTED: 0
ORIGINAL_HASH_CHANGES: 0
WORKCOPY_HASH_MISMATCHES: N/A (no workcopy created)
NEW_TESTS: 0
TEST_RESULT: 29/29 PASS (pre-existing synthetic-fixture suite, unrelated to this validation)
UNRESOLVED: GAME_ROOT (Windows local Steam path) is not reachable from this
  remote session; no real msg/res/grp files exist anywhere in this repo,
  session uploads, or filesystem as of this check.
NEXT_GATE: Cannot proceed past project-init/validate-path until real game
  files are either provided to this session or this pipeline is run in an
  environment with actual access to GAME_ROOT.
```
