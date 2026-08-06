# NOBU ToolHub — SSOT / Current Status

Governance Baseline Ⅴ.1나에 따른 진행 상황 문서. Foundation(`FOUNDATION_R1.md`)은
수정하지 않고, 이 문서만 세션마다 갱신한다. 인수인계 확인 순서(Governance Ⅴ.2):
Foundation → Governance(본 문서 상단이 아니라 FOUNDATION_R1.md의 Part 2) →
Current Status(본 문서) → 실행.

## 상태코드

- FOUNDATION: R1 (불변, 수정 없음)
- PROJECT_STATE: READY_FOR_PHASE1 → **PHASE1_IMPLEMENTED_PENDING_REVIEW**
- NOBU16 신뢰등급: CANDIDATE (CE 해당 여부 미확인, 추가 검증 필요 — 변경 없음)

## 이번 세션 변경 보고 (Governance Ⅳ.1)

**세션 시작 시 발견한 실제 상태**: 이 저장소(`tladi3284-dev/taishi`,
branch `claude/phase1-core-engine-impl-ug49do`)에는 NOBU ToolHub 관련 파일이
전혀 없었다. 세션 시작 전에 전달받은 "7개 모듈 중 3개 완료(logger_setup.py,
config_manager.py, version_resolver.py)" 상태는 이 저장소의 커밋 이력·워킹
트리 어디에서도 확인되지 않았고, 이 세션에서 접근 가능한 다른 GitHub
저장소도 없었다(`list_repos` 결과 `taishi` 1개뿐). 사용자에게 확인한 결과
**이 저장소에서 전부 새로 작성**하기로 결정했다 — 즉 "3개 완료" 상태는
이번 구현의 근거로 사용하지 않았다.

- **변경 파일**:
  - `NOBU_ToolHub/__init__.py`, `NOBU_ToolHub/launcher/{__init__.py, logger_setup.py,
    config_manager.py, version_resolver.py, game_path_finder.py, tool_manager.py, main.py}`
  - `NOBU_ToolHub/{tools,config,plugins,logs,workspace,cache}/.gitkeep` (Foundation R1 Ⅲ.3 디렉터리 스켈레톤)
  - `NOBU_ToolHub/docs/FOUNDATION_R1.md` (제공된 PDF 원문 전사, 이후 미수정)
  - `NOBU_ToolHub/docs/CURRENT_STATUS.md` (본 문서)
  - `tests/toolhub/test_*.py` (5개 핵심 모듈 단위 테스트)
  - `.gitignore` (런타임 산출물 — 로그/설정/캐시 — 제외 규칙 추가)

- **목적**: 사용자가 요청한 Phase 1 대상 5개 모듈(ConfigManager, ToolManager,
  VersionResolver, GamePathFinder, Logging Framework)과 프로젝트 스켈레톤을
  Foundation R1 / Governance Baseline에 정의된 아키텍처와 안전 원칙에 맞춰
  이 저장소에 새로 구현.

- **주요 내용**:
  - `logger_setup.py` — 회전 로그 파일(`NOBU_ToolHub/logs/toolhub.log`) + 콘솔
    핸들러, 멱등적 1회 구성.
  - `config_manager.py` — `GAME_CATALOG`(Foundation R1 Ⅲ.7 경로표 그대로),
    `TrustGrade` enum(Governance Ⅲ.2나), JSON 설정을 임시파일+`os.replace()`로
    원자적 저장(Governance Ⅱ.1가).
  - `game_path_finder.py` — Foundation R1 Ⅲ.5가의 5단계 감지 순서
    (Steam Library → libraryfolders.vdf → Registry → User Config → Manual
    Selection)를 각 단계 개별 메서드 + `locate()` 순차 시도로 구현. Windows
    레지스트리 조회는 `winreg` 부재 시(비-Windows) 조용히 건너뜀.
  - `version_resolver.py` — 시리즈 내 설정된 변형이 둘 이상이고 우선순위가
    없으면 `AmbiguousVersionError`로 즉시 중단(Governance Ⅱ.1나 Fail-Fast),
    경로를 추측해서 고르지 않음.
  - `tool_manager.py` — Foundation R1 Ⅲ.6나 시리즈↔도구 매핑, Ⅲ.1의 확인된
    도구 3종만 `KNOWN_TOOLS`에 등록(Font/Resource Tool 카테고리는 매핑표에는
    있으나 Ⅲ.1에 실측 실행 파일이 없어 임의로 지어내지 않음). `launch()`는
    실행 파일 미설정 시 `ToolNotConfiguredError`로 즉시 실패.
  - `main.py` — Phase 3 GUI 이전 단계에서 Core Engine을 검증할 최소 CLI
    (`list-games`, `list-tools`, `detect`, `set-path`, `resolve-version`).

- **잠재 영향**: 신규 파일만 추가되었고 기존 `localizer/` 코드는 전혀 건드리지
  않았다. 실제 Steam 설치 환경(Windows)이 없는 이 세션에서는 `GamePathFinder`의
  레지스트리/실제 라이브러리 탐색과 `ToolManager.launch()`의 실제 실행 파일
  구동 경로를 합성(synthetic) 픽스처로만 검증했다 — 실제 게임/도구 실행 파일에
  대한 검증은 아직 없다.

- **검증 결과**: `python -m pytest tests/toolhub -v` 결과는 본 문서 하단
  갱신 예정(커밋 전 실행). 기존 `tests/` (localizer) 전체도 회귀 여부 확인을
  위해 함께 실행한다.

## 추가 확인 사항 (Governance Ⅳ.1가 완료 기준 미충족 항목)

1. **Phase 번호 불일치**: Foundation R1 Ⅳ.2에는 "Phase 1 = Foundation
   (Architecture/Project Skeleton)", "Phase 2 = Core Engine(Tool Manager/
   Configuration Manager/Game Path Finder)"로 구분되어 있으나, 이번 세션에
   전달된 진행 상황 요약은 이 5개 모듈 전체를 "Phase 1(Core Engine)"으로
   지칭했다. Foundation 문서 자체는 수정하지 않았으므로, 이 번호 불일치는
   해석 차이인지 승인된 범위 변경인지 다음 세션에서 확인이 필요하다.
2. **NOBU16 CE 여부**: 여전히 미확인, CANDIDATE 등급 유지. 실제 게임 폴더
   내용을 읽기 전용으로 확인하기 전까지 AUTHORITATIVE/VERIFIED_SINGLE로
   격상하지 않는다.
3. **Phase 1 최종 PASS 승인**: 이 문서는 변경 보고이자 자체 검증 결과이지,
   승인 선언이 아니다. Governance Ⅳ.1가의 완료 기준 5개(요구사항 충족 /
   정상 동작 / 기존 기능 유지 / 검증 결과 제공 / 변경사항 명확 보고) 중
   앞의 4개는 이번 커밋으로 충족을 시도했으나, 실제 TASK_SPEC 원문 대조
   또는 별도 검증 세션의 PASS 판정은 여전히 대기 중이다.
4. **실제 Steam/Windows 환경 미검증**: 이 세션은 Linux 샌드박스이므로
   `GamePathFinder`/`ToolManager`는 단위 테스트(합성 픽스처)로만 검증됨.
   실제 PC에서의 자동 감지·도구 실행 검증은 별도로 필요하다.
