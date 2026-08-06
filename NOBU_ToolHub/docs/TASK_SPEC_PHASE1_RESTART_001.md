# TASK_SPEC: NOBU_TOOLHUB_PHASE1_RESTART_001

문서 위계(Governance Baseline Ⅴ.1나): `FOUNDATION_R1.md`(불변 기준) →
`FOUNDATION_R1.md` Part 2(운영 규범) → **본 문서(TASK_SPEC)** →
`CURRENT_STATUS.md`(SSOT, 세션마다 갱신).

작성일: 2026-08-06 · 작성 주체: Claude Code(초안) · 확정 주체: 사용자(검토·승인)
상태: **DRAFT — 사용자 확정 대기**

## 1. 배경 및 RESTART 사유

이전 세션 진입 시 "Phase 1(Core Engine) 7개 모듈 중 3개 완료(logger_setup.py,
config_manager.py, version_resolver.py)"라는 진행 상황이 보고되었으나, 이
저장소(`tladi3284-dev/taishi`)의 커밋 이력·워킹 트리 어디에서도 해당 산출물이
확인되지 않았고, 이 세션이 접근 가능한 다른 GitHub 저장소도 없었다
(`list_repos` 결과 `taishi` 1개뿐). 사용자 확인 후, 이 저장소에서 Foundation R1
기준으로 5개 Core Engine 모듈 + 스켈레톤을 전부 새로 구현했다(커밋 `88dd690`,
draft PR #2). 이 TASK_SPEC은 그 구현을 **공식 베이스라인으로 선언**하고,
Governance Baseline Ⅳ.1가의 완료 기준을 이 산출물에 대해 명시적으로 판정할 수
있는 근거 문서 역할을 한다. "RESTART"는 재작성이 아니라 — 문서화되지 않은
상태로 진행됐던 구현에 사후적으로 정식 TASK_SPEC을 부여하는 것이다.

## 2. 베이스라인 선언

다음을 Phase 1의 **현재 산출물(existing artifact)**로 선언한다. 이후 확정 시까지
이 파일들은 본 TASK_SPEC 검증 작업 범위에서 수정하지 않는다.

| 파일 | 역할 |
|---|---|
| `NOBU_ToolHub/launcher/logger_setup.py` | Logging Framework |
| `NOBU_ToolHub/launcher/config_manager.py` | Configuration Manager |
| `NOBU_ToolHub/launcher/version_resolver.py` | Version Resolver |
| `NOBU_ToolHub/launcher/game_path_finder.py` | Game Path Finder |
| `NOBU_ToolHub/launcher/tool_manager.py` | Tool Manager |
| `NOBU_ToolHub/launcher/__init__.py` | 패키지 export |
| `NOBU_ToolHub/launcher/main.py` | CLI 스켈레톤 (Phase 3 GUI 이전 검증용) |
| `NOBU_ToolHub/{tools,config,plugins,logs,workspace,cache}/` | Foundation R1 Ⅲ.3 디렉터리 스켈레톤 |
| `tests/toolhub/*.py` | 5개 핵심 모듈 단위 테스트 (33개) |

커밋: `88dd690` (`claude/phase1-core-engine-impl-ug49do`) · draft PR:
`tladi3284-dev/taishi#2` (base `claude/nobu11-p3-validation-c0ir2d`, 미머지)

## 3. 범위(Scope)

**포함**: Foundation R1 Ⅲ.2 아키텍처(Launcher → Tool/Configuration/Version/Path
관리자) 및 사용자가 최초 승인한 대상 목록 — ConfigManager, ToolManager,
VersionResolver, GamePathFinder, Logging Framework + 프로젝트 스켈레톤.

**제외(보류 범위, Foundation R1 Ⅳ.1가)**: 도구 내부 리팩터링, 기존 EXE 수정,
신규 메시지 편집기·텍스처 엔진 작성, GUI(PyQt6, Phase 3), 실제 게임/도구 파일에
대한 실행 검증(§6 참고).

### 3.1 Phase 번호 정의 (해소)

Foundation R1 Ⅳ.2는 "Phase 1 = Foundation(Architecture/Project Skeleton)",
"Phase 2 = Core Engine(Tool Manager/Configuration Manager/Game Path Finder)"로
구분한다. 그러나 이전 세션에 전달된 진행 상황 요약은 5개 Core Engine 모듈
전체를 "Phase 1"로 지칭했다. **본 TASK_SPEC은 이 프로젝트의 내부 트래킹
기준으로 "Phase 1"을 스켈레톤 + 5개 Core Engine 모듈(위 §2 베이스라인 전체)을
포괄하는 범위로 확정한다** — Foundation R1 원문의 장(章) 구분 자체는 수정하지
않되(Governance Ⅴ.1가), 실제 진행 관리에서는 이 정의를 따른다. 사용자가 본
TASK_SPEC을 확정하면 이 불일치는 더 이상 "미확인 사항"이 아니라 "기록된 결정"이
된다.

## 4. 완료 기준 (Governance Baseline Ⅳ.1가 5항목 구체화)

| # | 기준 | 이 산출물에서의 판정 근거 |
|---|---|---|
| 1 | 요구사항 충족 | §2 표의 7개 파일이 Foundation R1 Ⅲ.1/Ⅲ.5/Ⅲ.6/Ⅲ.7의 도구 목록·5단계 감지 순서·게임↔도구 매핑·경로표를 그대로 구현했는지 코드 대조 |
| 2 | 정상 동작 | `python3 -m pytest tests/toolhub -v` 전체 통과 + `python3 -m NOBU_ToolHub.launcher.main` CLI 수동 스모크 테스트 |
| 3 | 기존 기능 유지 | 기존 `localizer/` 관련 테스트(`tests/test_*.py`, `NOBU_ToolHub/` 제외)가 회귀 없이 통과 |
| 4 | 검증 결과 제공 | 본 문서 §6 사전 확인 결과 + `CURRENT_STATUS.md`의 pytest 실행 로그 |
| 5 | 변경사항 명확 보고 | `CURRENT_STATUS.md`의 "이번 세션 변경 보고" 절 (Governance Ⅳ.1 형식: 변경 파일/목적/주요 내용/잠재 영향/추가 확인 사항) |

5개 전부 충족되어야 완료로 간주한다(Governance Ⅳ.1가). **이 TASK_SPEC 문서
자체는 완료 판정이 아니라 판정 기준을 명시하는 것이며, 최종 PASS 승인은
사용자가 내린다.**

## 5. 신뢰등급 및 명시적 유보 사항

- **NOBU16 CE 여부**: 미확인 상태 유지(`TrustGrade.CANDIDATE`,
  `config_manager.py`의 `GAME_CATALOG_BY_KEY["NOBU16_PK"].note`). Phase 1
  완료 조건이 아니며, AUTHORITATIVE/VERIFIED_SINGLE로 격상하려면 실제 게임
  폴더의 읽기 전용 확인이 별도로 필요하다.
- **실제 Windows/Steam 환경 미검증**: 이 세션은 Linux 샌드박스이므로
  `GamePathFinder`(Steam Library/libraryfolders.vdf/Registry 단계)와
  `ToolManager.launch()`는 합성(synthetic) 픽스처로만 단위 테스트되었다.
  실제 PC에서의 자동 감지·도구 실행 확인은 Windows 환경이 있는 별도 세션에서
  수행해야 한다. 이 유보는 Phase 1 PASS를 막지 않는 기록된 한계로 취급한다.

## 6. 사전 확인(Pre-check) 절차 및 결과

사용자가 최초 요청한 "경로 존재 확인 + 기존 산출물 목록 보고(임의 수정 금지)"를
아래 명령으로 재현 가능하게 정의하고, 이번 TASK_SPEC 작성 시점 실행 결과를
기록한다(§2 베이스라인 파일은 수정하지 않았음).

```bash
git log --oneline -3
find NOBU_ToolHub -type f | sort
python3 -m pytest tests/ -q
```

실행 결과는 `CURRENT_STATUS.md`에 기록한다.

## 7. 승인 절차

본 문서는 DRAFT 상태로 커밋된다. 사용자가 내용을 검토 후 (a) 그대로 확정,
(b) 수정 요청, (c) 반려 중 하나를 선택하면 상단 상태 필드를 `CONFIRMED`로
갱신한다(이 갱신은 사용자 확정 이후 별도 커밋으로 반영). 이 문서의 확정 자체가
Phase 1 최종 PASS 승인을 의미하지 않는다 — PASS 승인은 §4 완료 기준 5항목에
대한 사용자의 별도 판단이다.
