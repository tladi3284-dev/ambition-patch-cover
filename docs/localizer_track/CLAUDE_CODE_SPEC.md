# 명세서: 《신장의 야망11 천하창세 PK》 자연 한글패치 워크벤치

이 문서는 Claude Code에 프로젝트 컨텍스트로 입력하기 위한 명세서다.
설계 원칙 → 실측으로 확인된 사실 → 현재 구현 상태 → 다음 작업 순서로 구성했다.
**추측이 아니라 실제로 검증된 것과 아직 안 풀린 것을 명확히 구분해서 적었다** —
Claude Code가 이 경계를 넘어 임의로 구현하지 않도록 하는 것이 이 문서의 핵심 목적이다.

---

## 0. 프로젝트 정체성

```yaml
PROJECT_ID: NOBUNAGA11PK_NATURAL_KOREAN_PATCH
APPLICATION_TYPE: REVERSE_ENGINEERING_LOCALIZATION_WORKBENCH
GAME_ROOT: 'C:\Program Files (x86)\Steam\steamapps\common\Nobunaga11WPK'
CURRENT_PHASE: P3
CURRENT_STAGE: LOGICAL_MESSAGE_SPAN_AND_CONTROL_CODE_ANALYSIS
```

이 앱은 단순 번역기나 바이너리 편집기가 아니다. `msg`/`res`/`SCEDA`/`DBSCEDA`/
`FONT` 리소스에서 일본어를 추출하고, 자연스러운 한국어로 번역·검수한 뒤,
검증된 구조 규칙에 따라 **작업 사본**을 재구축하는 통제형 한글화 플랫폼이다.

Steam 원본 폴더를 자동으로 덮어쓰는 프로그램이 **아니다.**

---

## 1. 절대 안전 원칙 (모든 코드가 지켜야 함)

1. **원본 읽기 전용** — `original_source_path`(Steam 설치 경로)는 읽기·해시
   계산·복사만 허용한다. 쓰기·삭제·이름변경은 코드 레벨에서 항상 차단한다.
2. **작업 사본 분리** — 모든 재구축·시험은 별도 `workcopy_path`에서만
   수행한다. `workcopy_path`가 `original_source_path` 안쪽 경로가 되는 것을
   막는다 (Steam 폴더 안에 작업 폴더를 실수로 만들지 않는다).
3. **단계별 쓰기 잠금** — 구조가 검증되지 않은 파일 형식에는 쓰기 기능을
   제공하지 않는다. `support_status`가 `SUPPORTED`가 아니면 쓰기 금지.
4. **승인 번역만 삽입** — 번역 상태는
   `NOT_TRANSLATED → DRAFT → REVIEW_REQUIRED → HISTORY_REVIEWED → UI_REVIEWED → APPROVED`
   순서를 반드시 지킨다. 단계 건너뛰기·역행은 예외로 막는다.
   `APPROVED`가 아닌 번역은 재구축 입력으로 쓸 수 없다.
5. **결정론적 빌드** — 같은 원본·설정·번역 코퍼스·코드표·폰트로 빌드하면
   결과 파일 SHA-256이 항상 같아야 한다. `UNEXPECTED_CHANGES: 0`.
6. **추측 금지** — 검증되지 않은 바이너리 구조(포인터 의미, 제어 코드
   카탈로그 등)를 추측으로 구현하지 않는다. 모르는 것은 `NotImplementedError`
   또는 `CONDITIONAL` 상태로 명시하고, 실제 관찰 근거가 쌓이면 그때 채운다.

---

## 2. 실측으로 확인된 사실 (2026-07-31, 실제 게임 파일 기준)

아래는 추측이 아니라 실제 `msg/*.n11` 파일(71개, `grp.7z` 아카이브에서 확보)을
직접 열어서 검증한 내용이다. `localizer/msg_viewer.py`의 파서가 이 내용을
실제로 구현하고 있다.

### 2.1 일반 계열 (69개 파일) — `MSG_N11F_TEXT_PLUS_POINTER_TABLE`

```
offset 0..3      : magic b"N11F"
offset 4..7      : LE uint32 = 포인터 테이블이 시작하는 절대 파일 오프셋(T)
offset 8..T-1    : CP932 평문 텍스트 구간 — 암호화(XOR) 없음, 69/69 정상 디코딩 확인
offset T-4..T-1  : 고정 경계 마커 b"\x0a\x1f\x2c\x0a" (69개 파일 전부 동일)
offset T..EOF    : 4바이트 LE uint32 포인터 테이블. (EOF-T) % 4 == 0 전부 성립.
                   각 항목 상위 16비트는 파일마다 거의 동일(예: 0xe979) —
                   절대 주소를 구운(baked) 포인터로 추정.
```

> **설계서의 "XOR 암호화" 가정은 틀렸다.** 실측 결과 암호화가 전혀 없다.
> `format_classifier.py`는 이미 이에 맞춰 이름과 근거를 수정했다.

### 2.2 `yabou.n11` 변형 — `MSG_YABOU_ASCII_DECIMAL`

```
offset 8..9250     : 텍스트 구간1 (일반 계열과 동일한 CP932 태그 형식)
offset 9251..9254  : 고정 경계 마커 (일반 계열과 동일)
offset 9255..11742 : 8자리 ASCII 10진수 × 311개
                      - 앞 4개(관찰값: 308, 26292, 0, 0): 헤더성 값, 의미 미상
                      - 나머지 307개: 텍스트1 안의 바이트 오프셋 (MSG 태그
                        수 306개와 거의 일치, 1개 차이 원인 미상)
offset 11743..EOF  : 두 번째 텍스트 블록. 자체 헤더 없음, ",,Error"로 시작,
                      EOF까지 CP932로 100% 정상 디코딩 (에러 메시지 추정).
```

### 2.3 아직 안 풀린 것 (P3 게이트로 남음 — 추측 금지, 실측으로만 닫을 것)

- 포인터 테이블 항목과 텍스트 구간 내 "논리 메시지 범위"의 정확한 대응
  관계 (항목 수가 MSG 태그 수보다 7~9배 많음 — 태그당 여러 항목이 붙는
  것으로 보이나 규칙 미확정)
- 쉼표로 구분된 토큰 중 어떤 게 제어 코드/변수이고 어떤 게 순수 대사인지
  (제어 코드 카탈로그 없음)
- yabou.n11 헤더성 4개 값의 의미, 307 vs 306 개수 불일치 원인
- yabou.n11 두 번째 텍스트 블록 전용 오프셋 테이블이 따로 있는지
- 재구축(쓰기) 시 포인터를 어떻게 갱신할지 — 텍스트 길이가 바뀌면 오프셋이
  전부 밀리므로, 쓰기 로직은 아직 구현하지 않았음 (의도적)
- `SCEDA`/`DBSCEDA`/`res` 이미지 컨테이너 — 아직 샘플 미분석, 구조 완전 미상
- `FONT.N11`/`FONT12.N11` 글리프 포맷 — 미분석

**닫는 방법**: 후보 오프셋/태그를 뽑은 뒤 실제 게임을 실행해 화면에 뜨는
문구와 대조한다. 검증되지 않은 상태로 파싱/재구축 로직을 추측으로 채우면
`DETERMINISTIC_BUILD_REQUIRED` 요구사항과 정면 충돌한다.

---

## 3. 현재 구현 상태

Python 패키지 `localizer/` (경로: 이 문서와 같은 폴더 기준 `localizer/`)에
아래 모듈이 **구현·테스트 완료** 상태다 (pytest 44개 전부 통과).

| 모듈 | 파일 | 상태 |
|---|---|---|
| 프로젝트 관리자 | `project_manager.py` | 완료 — 원본=작업사본 경로 금지 강제 |
| 경로·판본 검사기 | `path_validator.py` | 완료 — 읽기 전용, 판본은 추측 안 함 |
| 기준선 관리자 | `baseline_manager.py` | 완료 — SHA-256 매니페스트, diff |
| 작업 사본 생성기 | `workcopy_creator.py` | 완료 — 포함관계 차단, 복사후 해시검증 |
| 파일 스캐너/분류기 | `file_scanner.py`, `format_classifier.py` | 완료 — 미검증 포맷은 항상 CONDITIONAL/UNKNOWN |
| msg N11F 파서 | `msg_viewer.py` | 완료(일반+yabou 변형) — §2 실측 구조 반영 |
| 번역 코퍼스 | `translation_schema.py` | 완료 — 상태 게이트, 제어코드/플레이스홀더 손실 검증 |
| 용어집 | `glossary_manager.py` | 완료 — CRUD, 충돌 검사 |
| res 인벤토리 | `res_inventory.py` | 완료 — 읽기 전용 목록화만 |
| 이미지 조사 뷰어 | `image_research_viewer.py` | 완료 — 표준 포맷만 메타데이터 추출 |
| CLI | `cli.py` | 완료 — 위 전부를 command로 노출 |

**의도적으로 구현하지 않은 것** (§2.3의 미해결 항목에 의존하므로):
- 자동 번역 삽입 / 배포용 재구축 엔진
- FONT/이미지 리소스 쓰기
- 실시간 게임 패처

---

## 4. Claude Code에게 지시하는 다음 작업

우선순위 순서. **각 항목은 실제 관찰/실험 결과가 코드에 남아야 완료로 친다**
(추측성 구현 금지, §1-6 참고).

### 4.1 (최우선) 논리 메시지 범위 규칙 실험
- `localizer/msg_viewer.find_msg_tag_candidates()`로 MSG 태그 위치를 뽑고,
  포인터 테이블 항목(`read_n11f_container().read_pointer_table_u32()`)과
  개수·순서를 여러 파일에 걸쳐 대조하는 실험 스크립트를 `scripts/` 아래
  새로 작성할 것. 목표: "포인터 N개가 태그 1개에 대응한다"는 가설을
  파일 간 비교로 검증하거나 반증한다.
- 결과는 `localizer/msg_viewer.py` 상단 docstring에 실측 근거와 함께 반영.

### 4.2 제어 코드 카탈로그 착수
- 텍스트 구간의 쉼표 구분 토큰을 전수 조사해서 빈도표를 만드는 유틸리티
  (`localizer/control_code_survey.py` 제안)를 추가. 어떤 토큰이 태그성
  키워드(`MSG`, `bp1`, `din` 등)이고 어떤 게 실제 대사인지 통계적으로 분리.
- 이건 여전히 "관찰 도구"이지 "확정된 카탈로그"가 아니다 — 사람이 검토할
  후보 목록을 만드는 단계.

### 4.3 `res` 폴더 이미지 컨테이너 조사
- 실제 `res/*.N11` 샘플이 아직 없다면, 사용자에게 요청할 것.
- 확보되면 `res_inventory.py`에 시그니처 기반 1차 분류를 추가하되,
  `SUPPORTED`로 단정하지 말고 `format_classifier.py`와 동일한 원칙
  (미검증 = CONDITIONAL/UNKNOWN)을 따를 것.

### 4.4 FONT.N11 / FONT12.N11 조사
- 아직 미착수. 문서 §2.3 참고. 샘플은 이미 `grp.7z` 안에 있음
  (`grp/FONT.N11`, `grp/FONT12.N11` — 아직 추출·분석 안 함).

### 4.5 삼가야 할 것
- msg 파일의 쓰기(재구축) 로직을 지금 단계에서 구현하지 말 것 — 포인터
  갱신 규칙이 안 풀렸으므로, 지금 쓰면 파일이 깨진다.
- 실제 게임 저작권 자산(msg/res/grp 원본 바이트)을 테스트 픽스처로 커밋하지
  말 것. 테스트는 항상 `tests/test_*.py`처럼 합성(synthetic) 바이트로 작성.

---

## 5. 코딩 규칙 (기존 코드베이스와 일관성 유지)

- 모든 신규 파서/분류 함수는 "왜 이 상태로 뒀는지"를 docstring에 실측
  근거와 함께 남길 것 (`msg_viewer.py`, `format_classifier.py` 참고 스타일).
- 원본 파일에 쓰기 함수는 반드시 `workcopy_creator.py`의 안전장치
  (경로 포함관계 차단, 해시 검증)를 재사용하거나 동등한 검증을 넣을 것.
- 새 포맷 분류는 근거 없이 `SUPPORTED`를 주지 말 것 —
  `tests/test_format_classifier.py::test_no_format_is_ever_plain_supported`
  같은 회귀 테스트로 이 원칙을 고정해 둘 것.
- 번역 관련 코드는 `translation_schema.py`의 상태 게이트를 절대 우회하지
  말 것 (건너뛰기/역행 금지, 제어코드·플레이스홀더 손실 시 저장 거부).
- pytest로 회귀 테스트를 먼저 쓰고 구현할 것. 저작권 있는 게임 데이터가
  아니라 합성 픽스처를 사용할 것 (`tests/test_msg_viewer.py`의
  `_build_synthetic_n11f`, `_build_synthetic_yabou` 패턴 참고).

---

## 6. 디렉터리 구조 (현재)

```text
localizer/
  models.py                  # 문서 스키마 → dataclass
  project_manager.py          # 프로젝트 생성/로드, 원본=작업사본 금지
  path_validator.py           # 게임 루트·msg·res 경로 검사 (읽기전용)
  baseline_manager.py         # SHA-256 기준선, diff
  workcopy_creator.py         # 안전한 작업 사본 복사
  format_classifier.py        # 시그니처 기반 1차 분류 (정직한 UNKNOWN/CONDITIONAL)
  file_scanner.py             # 스캔+분류 파이프라인, CSV/JSON 산출물
  msg_viewer.py                # N11F 구조 파서 (일반+yabou 변형, 실측 검증됨)
  translation_schema.py       # 번역 코퍼스, 상태 게이트
  glossary_manager.py         # 용어집 CRUD
  res_inventory.py            # res 폴더 읽기 전용 인벤토리
  image_research_viewer.py    # 표준 이미지 포맷 메타데이터 (Pillow)
  cli.py                      # 전체 CLI
tests/
  test_project_manager.py
  test_path_validator.py
  test_workcopy_creator.py
  test_format_classifier.py
  test_msg_viewer.py
  test_translation_schema.py
requirements.txt
README.md                     # 사용법 + 실측 결과 상세
CLAUDE_CODE_SPEC.md            # 이 문서
```

## 7. CLI 명령 레퍼런스

```bash
python -m localizer.cli project-init --root <dir> --original-source <path> \
  --workcopy <path> --backup <path> --output <path>
python -m localizer.cli validate-path --game-root <path>
python -m localizer.cli scan --root <dir>
python -m localizer.cli make-workcopy --root <dir> [--allow-existing]
python -m localizer.cli res-inventory --root <dir> --res-path <path>
python -m localizer.cli glossary-add --root <dir> --ja <원문> --ko <번역> [--category ...]
python -m localizer.cli corpus-status --root <dir>
python -m localizer.cli msg-inspect --file <path> [--find-strings] [--min-len N]
python -m localizer.cli status --root <dir>
```
