# NOBU ToolHub Project Foundation & Governance Baseline

신장의 야망 시리즈 통합 런처 프로젝트 — Foundation R1 · Governance Baseline
문서 생성일: 2026-08-06

> 본 문서는 `NOBU_ToolHub_Foundation_Governance_R1.pdf` 원문의 전사(transcription)이다.
> Governance Baseline Ⅴ.1가에 따라 **Part 1(Foundation)은 이후 수정하지 않는다.**
> 확장이 필요하면 기존 조항을 고치지 않고 해당 장(章) 내 항목을 추가하는 방식으로만 반영한다.
> 진행 상황·이슈·다음 액션은 이 문서가 아니라 `CURRENT_STATUS.md`(SSOT)에서 관리한다.

본 문서는 NOBU ToolHub 프로젝트의 두 상위 기준 문서(Part 1. Foundation, Part 2.
Governance)를 하나로 통합한 것이다. Foundation은 프로젝트 목표·설계 원칙·아키텍처·지원 시리즈
경로를 정의하는 불변 기준선이며, Governance는 이를 운영하는 안전 원칙·상태 관리 체계·변경
절차·문서 관리 규범이다. 이후 구현이 진행되어도 본 문서 자체는 수정하지 않으며, 진행 상황은
별도의 SSOT / Current Status 문서로 관리한다.

## Part 1. Project Foundation (R1)

### Ⅰ. 프로젝트 개요

1. 프로젝트명: NOBU ToolHub
   1. 유형: 범용 다중 도구 통합 플랫폼(Universal Multi-Tool Integration Platform)
   2. 상태: FOUNDATION_BASELINE / 현재 단계 ANALYZE / Revision Foundation R1
2. 목표
   1. 여러 개의 독립적인 NOBU 시리즈 지원 도구를 하나의 통합 환경에서 관리
   2. 사용자는 개별 프로그램을 각각 실행·설정할 필요 없이 하나의 런처에서 선택 실행
   3. 기존 프로그램의 코드와 동작 방식은 일체 수정하지 않고, 통합 계층만 추가

### Ⅱ. 설계 원칙

1. 기존 도구 보존
   1. 모든 실행 파일은 원본 그대로 유지, 내부 코드 미수정, 기존 기능 제거 없음
2. Wrapper 구조
   1. 런처는 Wrapper 역할만 수행하며 각 도구는 독립 실행
   2. 런처 담당 범위: Tool Discovery / Configuration / Version Selection / Logging / Path Management
3. 비파괴적 통합
   1. 기존 프로젝트와 충돌 없는 Overlay 방식으로 신규 구조 추가
4. 공용 리소스
   1. 중앙화 대상: Plugins, Configuration, Logs, Documentation

### Ⅲ. 확인된 분석 및 아키텍처

1. 확인된 도구 목록
   1. Tool 1 — Picture Editor v1.20, 공용 Plugins 사용
   2. Tool 2 — Picture Editor Extended v1.24_HAN, Python 기반(CLI+GUI), 공용 Plugins 사용
   3. Tool 3 — Message Editor, C#/Windows Forms, SJIS Table 기반, 독립 구조
2. 초기 아키텍처
   1. NOBU ToolHub → Launcher(Tool Manager / Configuration Manager / Version Resolver / Game Path Finder) → Picture Tools / Message Tools / Resource Tools → 원본 실행 파일
3. 초기 디렉터리 구조
   1. NOBU_ToolHub/ 하위: launcher, tools, config, plugins, logs, docs, workspace, cache
4. 지원 시리즈 및 Steam 경로 구조
   1. 1차 지원 대상: NOBU11(천하창세 PK) ~ NOBU16(어웨이크닝/CE) — 이후 시리즈 확장 가능한 구조로 설계
   2. Games/ 하위에 NOBU01~NOBU16(각 PK/CE 등 확장판 포함) 폴더 구조로 관리
5. 자동 감지 순서
   1. 1) Steam Library → 2) Steam libraryfolders.vdf → 3) Registry → 4) User Config → 5) Manual Selection
   2. Steam 최신 Windows판은 라이브러리 설정 파일을 통한 설치 위치 확인이 일반적인 방식
6. 설정 및 도구 매핑
   1. Configuration [Games] 섹션에 NOBU11~NOBU16(및 PK 버전) 경로 키 관리
   2. 게임별 도구 매핑
      1. NOBU11 — Msg Editor, Font Tool, Resource Tool
      2. NOBU12 — Msg Editor, Picture Tool
      3. NOBU13 — Msg Editor, Picture Tool
      4. NOBU14 — PicTool, Msg Editor, Resource Tool
      5. NOBU15 — Msg Editor, Picture Tool, Resource Tool
      6. NOBU16 — Msg Editor, Resource Tool
7. PC 실제 소장 경로 [확인됨] (기준: `C:\Program Files (x86)\Steam\steamapps\common\`)
   1. NOBU11_TENKASOUSEI_PK → `\Nobunaga11WPK`
   2. NOBU12_KAKUSHIN_PK → `\NOBUNAGA'S AMBITION Kakushin with Power Up Kit`
   3. NOBU13_TENDO_PK → `\NOBUNAGA'S AMBITION Tendou with Power Up Kit`
   4. NOBU14_SPHERE_OF_INFLUENCE(기본판) → `\Nobunaga's Ambition Souzou`
   5. NOBU14_SPHERE_OF_INFLUENCE_ASCENSION(확장판) → `\NOBUNAGAS_AMBITION_Souzou_SengokuRisshiden`
   6. NOBU15_TAISHI_PK → `\NOBUNAGAS_AMBITION_TAISHI`
   7. NOBU16_PK → `\NOBU16` [추가 검증 필요: CE 해당 여부 미확인]
   8. 미보유: NOBU01~NOBU10
   9. 시리즈 외 게임(관리 대상 아님): Romance of the Three Kingdoms 13, SAN8R(삼국지8 리메이크)

### Ⅳ. 범위 및 개발 단계

1. 활성 범위: Launcher / Configuration / Version Management / Game Detection / Logging / Tool Execution
   1. 보류 범위: 도구 내부 리팩터링, 기존 EXE 수정, 신규 메시지 편집기·텍스처 엔진 작성
2. 개발 단계
   1. Phase 1 — Foundation(Architecture / Project Skeleton)
   2. Phase 2 — Core Engine(Tool Manager / Configuration Manager / Game Path Finder)
   3. Phase 3 — GUI(PyQt6 — Launcher / Settings / Log Viewer)
   4. Phase 4 — Integration(Version Resolver / Shared Plugins / Migration)
   5. Phase 5 — QA(Testing / Regression / Packaging)
   6. Phase 6 — Release(PyInstaller / Documentation / Installer)

### Ⅴ. 성공 기준 및 현재 상태

1. 성공 기준: 기존 도구 무수정 통합 실행, 게임 경로 자동 감지, 버전 선택, 설정 일원화, 공용 Plugins 관리,
   로그·오류 추적, Windows 11 안정 동작, 기존 프로젝트 100% 호환
2. 현재 상태
   1. FOUNDATION: R1 / USER_STAGE: ANALYZE / STATUS: READY_FOR_PHASE1
   2. NEXT_ACTION: Project Skeleton 설계 및 Core Engine 구조 생성

## Part 2. Governance Baseline

### Ⅰ. 거버넌스 개요

1. 목적: 여러 세션·여러 실행 Agent(Claude Code / Codex / Antigravity)에 걸쳐 프로젝트를 진행해도 기준이
   흔들리지 않도록 하는 상위 규범 확립
   1. 적용 범위: NOBU ToolHub Launcher / Core Engine / GUI / Integration / QA / Release 전 단계
   2. 문서 위계: Foundation(불변 기준) → Governance(운영 규범, 본 파트) → SSOT / Current Status(진행 상황, 세션마다 갱신)

### Ⅱ. 안전 원칙

1. 원본 보호 원칙(시리즈 공통 4개축 중 적용)
   1. 임시파일 + 원자적 교체 방식으로만 파일 변경(직접 덮어쓰기 금지)
   2. Fail-Fast — 실패 시 쓰기 전 중단, 이미 쓴 경우 역순 롤백
   3. 결정론적 처리 — 동일 입력 → 동일 출력/해시 보장
   4. 타 프로젝트 산출물 재사용 범위 — 배포 방식·검증 절차 원칙은 재사용 가능하나, 실행파일·경로·해시·오프셋·우회 방식의 직접 재사용은 금지
2. 개발 원칙 12개 준수
   1. 명세 우선 / 최소 변경 / 기존 구조 존중 / 안정성 우선 / 가독성 / 중복 최소화 / 검증 / 변경 보고 / 오류 대응(추측 수정 금지) / 자동화(검증 가능한 형태) / 보안(민감정보 하드코딩 금지) / 문서화
3. 우선순위: 정확성 → 안정성 → 유지보수성 → 성능 → 편의성

### Ⅲ. 상태 관리 체계

1. Stage 구조(시리즈 공통 P0~P8 체계를 ToolHub에도 적용)
   1. 현재 위치: NOBU ToolHub = P0(Foundation/기준본 확정 단계), Phase 1(Architecture / Project Skeleton) 착수 대기
2. 상태코드
   1. 프로젝트 전체 상태: FOUNDATION_BASELINE → ANALYZE → READY_FOR_PHASE1(현재)
   2. 개별 도구 연동 신뢰등급(순정 프로필 기준 준용): AUTHORITATIVE(원본 그대로 실행 확인됨) / VERIFIED_SINGLE(1회 검증) / CANDIDATE(미검증 매핑) / UNTRUSTED(경로·버전 미확인)
   3. 현재 NOBU16은 CE 여부 미확인 상태로 CANDIDATE 등급 적용

### Ⅳ. 변경 및 검증 절차

1. 변경 보고 형식: 변경 파일 / 목적 / 주요 내용 / 잠재 영향 / 추가 확인 사항 순으로 기록
   1. 완료 기준 — 요구사항 충족 + 정상 동작 + 기존 기능(개별 도구 원본) 유지 + 검증 결과 제공 + 변경사항 명확 보고, 5개 모두 충족해야 완료로 간주
2. 금지 사항
   1. 요구사항 임의 변경, 미확인 내용을 확정처럼 기술, 검증 없이 완료 선언, 불필요한 리팩터링, 원본 도구 손상 변경, 기록 없는 파일 변경 종료

### Ⅴ. 문서 관리 및 인수인계

1. Foundation 문서(Part 1)는 이후 수정하지 않음
   1. 확장 시에도 기존 조항 변경이 아니라 해당 장(章) 내 항목 추가로만 반영(예: Ⅲ장 경로 목록 확장 사례)
   2. 진행 상황·이슈·다음 액션은 별도 SSOT / Current Status 문서에서 관리하며, 세션이 바뀌어도 본 문서 기준으로 이어받음
2. 다음 세션 인수인계 시 확인 순서
   1. Foundation(목표·원칙) → Governance(본 문서, 안전원칙·상태코드) → Current Status(마지막 진행 지점) → 실행
