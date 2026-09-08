# NOBU11PK 천하창세 PK 한국어 패치

이 저장소는 **《신장의 야망 11 PK / 천하창세 PK》 한국어 패치의 공식 배포·안내 저장소**입니다.

## 현재 배포 기준

- 배포 버전: **v1.0.19**
- 최종 실행 대상: 지정 노트북
- USB 최종 배포 보관소: `D:\NOBU11PK_KOREAN_PATCH\`
- 최종 패키지 ZIP: `NOBU11PK_KoreanPatch_1.0.19.zip`
- ZIP SHA-256: `70f6ea182624681330b14a13a021d82944153a05e3e750a854dbf53e487d4063`
- USB 패키지 검증: **PASS**
- 실제 게임 기동/시작 메뉴 런타임 검증: **PASS**

> GitHub Release의 ZIP 자산 업로드는 별도 게시 단계입니다. 이 저장소의 문서와 체크섬은 현재 검증된 v1.0.19 배포 기준을 설명합니다.

## 설치 및 실행

1. Steam에서 《신장의 야망 11 PK / 천하창세 PK》가 정상 설치되어 있는지 확인합니다.
2. 배포 패키지를 원하는 위치에 압축 해제합니다.
3. `NOBU11PK_KoreanPatch.exe`를 실행합니다.
4. 런처에서 **한글판 실행**을 사용해 게임을 실행합니다.
5. 런타임 문자열 패치가 필요한 항목은 반드시 한국어 패치 런처를 통해 실행해야 합니다.

자세한 내용은 [`docs/설치_및_사용_설명서.md`](docs/설치_및_사용_설명서.md)를 참고하십시오.

## 중요: Steam 무결성 검사

Steam의 **게임 파일 무결성 검사 / 설치 파일 확인·복구**를 실행하면 한국어 패치가 적용된 게임 파일이 일본어 원본으로 복구될 수 있습니다.

실제 검증에서 패치 대상 107개 파일이 모두 원본 상태로 복구되는 현상이 확인되었습니다. 이런 작업을 수행한 경우 기존 런타임 PASS 상태를 그대로 신뢰하지 말고, 최신 검증 패키지를 다시 설치한 뒤 런타임 검증을 수행해야 합니다.

## 배포물 무결성

배포 ZIP의 SHA-256은 [`SHA256SUMS.txt`](SHA256SUMS.txt)에서 확인할 수 있습니다.

이 저장소에는 원본 게임 실행 파일이나 저작권이 있는 원본 게임 데이터의 배포를 목적으로 하지 않습니다. 패치·런처·설명서 등 배포에 필요한 자료만 관리합니다.

---

# 개발/워크벤치 정보

아래 내용은 한국어 패치의 리버스 엔지니어링 및 현지화 워크벤치에 관한 개발 정보입니다.

《信長の野望11 天下創世PK》("Nobunaga's Ambition 11: Souzou no Tenka PK") 자연
한글패치를 위한 리버스 엔지니어링/현지화 워크벤치. 단순 번역기·바이너리
에디터가 아니라, `msg`/`res`/`grp` 리소스에서 일본어를 추출하고 자연스러운
한국어로 번역·검수한 뒤, 검증된 구조 규칙에 따라 **작업 사본**을 재구축하는
통제형 플랫폼이다. 상세 설계 원칙과 실측 근거는 `docs/localizer_track/CLAUDE_CODE_SPEC.md`
참고.

Steam 원본 폴더를 자동으로 덮어쓰지 않는다 — 모든 재구축·시험은 별도
workcopy에서만 수행한다.

## 빠른 시작

```bash
pip install -r requirements.txt
python3 -m pytest tests/ -v

# 1) 프로젝트 초기화 (원본/작업사본/백업/출력 경로 등록)
python3 -m localizer.cli project-init \
  --root <project-dir> \
  --original-source <Steam game folder> \
  --workcopy <workcopy dir> \
  --backup <backup dir> \
  --output <output dir>

# 2) 게임 경로 검증 (읽기 전용)
python3 -m localizer.cli validate-path --game-root <Steam game folder>

# 3) 파일 스캔/분류 (원본, 읽기 전용)
python3 -m localizer.cli scan --root <project-dir>

# 4) 작업 사본 생성 (복사 후 해시 검증)
python3 -m localizer.cli make-workcopy --root <project-dir>

# 5) msg/*.n11 구조 확인
python3 -m localizer.cli msg-inspect --file <msg-file> --find-strings

# 6) 현재 상태 확인
python3 -m localizer.cli status --root <project-dir>
```

## 안전장치

1. **원본 읽기 전용** — `original_source_path`는 어떤 CLI 명령으로도 쓰기/삭제/
   이름변경할 수 없다. `workcopy_creator`와 `baseline_manager`는 항상 읽기만
   수행한다.
2. **작업 사본 분리** — `project_manager.create_project`와
   `workcopy_creator.make_workcopy` 둘 다 `workcopy_path`가
   `original_source_path`와 같거나 그 하위 경로면 `ProjectPathConflictError`로
   즉시 거부한다.
3. **단계별 쓰기 잠금** — `format_classifier`는 시그니처만으로는 절대
   `SUPPORTED`를 주지 않는다 (`SupportStatus.CONDITIONAL`/`UNKNOWN`만 부여).
   `test_no_format_is_ever_plain_supported`가 이 원칙을 회귀 테스트로 고정한다.
4. **승인 번역만 삽입** — `translation_schema.TranslationCorpus`는
   `NOT_TRANSLATED → DRAFT → REVIEW_REQUIRED → HISTORY_REVIEWED → UI_REVIEWED →
   APPROVED` 순서만 허용하며 건너뛰기/역행 시 `InvalidStatusTransitionError`를
   낸다. `APPROVED` 승격 시 원문·번역문의 제어코드/플레이스홀더가 다르면
   `ControlCodeLossError`로 거부한다.
5. **결정론적 빌드** — `baseline_manager`는 SHA-256 매니페스트와 diff만
   제공한다. `workcopy_creator.make_workcopy`는 복사 후 원본·작업사본의
   매니페스트가 완전히 일치하는지 재확인하고, 다르면
   `WorkcopyHashMismatchError`를 낸다.
6. **추측 금지** — 실측되지 않은 바이너리 구조는 코드로 단정하지 않는다.
   `msg_viewer.py`의 docstring에 실측 근거와 미해결 항목을 명시했다.

## msg N11F 포맷 (실측 결과)

`localizer/msg_viewer.py` 상단 docstring 참고. 요약:

- 일반 계열(69개 파일): `N11F` 매직 + LE uint32 포인터 테이블 오프셋 + CP932
  평문(암호화 없음) + 고정 경계 마커 `0a 1f 2c 0a` + LE uint32 포인터 테이블.
- `yabou.n11` 변형: 텍스트 구간1(오프셋 8~9250) + 경계 마커(9251~9254) +
  8자리 ASCII 10진수 311개(9255~11742, 앞 4개는 헤더성, 나머지 307개는 텍스트1
  내 오프셋으로 추정) + 두 번째 텍스트 블록(11743~EOF, `,,Error`로 시작).
- 아직 안 풀린 것(추측 금지, P3 게이트로 남김): 포인터-태그 대응 규칙, 제어
  코드 카탈로그, yabou 헤더 4값의 의미, 307 vs 306 불일치 원인, 재구축 시
  포인터 갱신 규칙. 쓰기(재구축) 경로는 의도적으로 미구현.

## 디렉터리 구조

```text
localizer/
  models.py                  # 문서 스키마 -> dataclass/enum
  project_manager.py          # 프로젝트 생성/로드, 원본=작업사본 금지
  path_validator.py           # 게임 루트/msg/res 경로 검사 (읽기전용)
  baseline_manager.py         # SHA-256 기준선, diff
  workcopy_creator.py         # 안전한 작업 사본 복사 + 사후 해시 검증
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
README.md
docs/localizer_track/CLAUDE_CODE_SPEC.md
```

## CLI 명령 레퍼런스

```bash
python -m localizer.cli project-init --root <dir> --original-source <path> \
  --workcopy <workcopy dir> --backup <backup dir> --output <output dir>
python -m localizer.cli validate-path --game-root <path>
python -m localizer.cli scan --root <dir>
python -m localizer.cli make-workcopy --root <dir> [--allow-existing]
python -m localizer.cli res-inventory --root <dir> --res-path <path>
python -m localizer.cli glossary-add --root <dir> --ja <원문> --ko <번역> [--category ...]
python -m localizer.cli corpus-status --root <dir>
python -m localizer.cli msg-inspect --file <path> [--find-strings] [--min-len N]
python -m localizer.cli status --root <dir>
```

## 의도적으로 구현하지 않은 것

- msg 파일 쓰기(재구축) 로직 — 포인터 갱신 규칙이 실측으로 닫히기 전까지.
- `res`/`SCEDA`/`DBSCEDA`/`FONT.N11`/`FONT12.N11` 파서 — 샘플 미분석.
- 자동 번역 삽입 / 배포용 재구축 엔진 / 실시간 게임 패처.

## 테스트 픽스처 원칙

모든 테스트는 저작권이 있는 실제 게임 바이트를 커밋하지 않고, 합성
(synthetic) 바이트만 사용한다 (`tests/test_msg_viewer.py`의
`_build_synthetic_n11f`, `_build_synthetic_yabou` 참고).
