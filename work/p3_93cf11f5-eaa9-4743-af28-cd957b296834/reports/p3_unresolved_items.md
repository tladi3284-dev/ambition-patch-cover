# P3 Unresolved Items (사용자 결정 / 후속 조치 필요)

## 1. 입력 자료 부재 (최우선, P3 진행 자체를 막음)
- `p2_screen_mapping.json` 등 P2 산출물 부재 → `reports/p2_gap_report.md` 참조
- P1 산출물(`pilot_scenario_strings.json` 등) 부재
- `hangul_code_map.json` 및 실제 인코더 부재
- 순정 SCEDA 7종 / FONT.N11 / FONT12.N11 / EXE 원본 부재

## 2. 사용자 결정 필요 (인수인계서에서 이미 표시된 항목)
- **SCENARIO_TITLE_003**: "노부나가 포위망" vs "신장 포위망" — 프로젝트 전체
  인물명 표기 정책(자연 번역 우선 vs 한자음 정책 일관성)에 따라 결정 필요.
- **SCENARIO_TITLE_005**: 가운뎃점 "·" 사용 여부 및 슬롯 초과 시 대체안
  ("코마키·나가쿠테 전투" / "코마키-나가쿠테 전투" / "코마키 나가쿠테 전투" /
  "코마키·나가쿠테") — 21바이트 슬롯 검사가 완료된 후에도 최종 선택은 사용자
  몫.
- **SCENARIO_TITLE_006**: "마사무네의 반격" vs "마사무네의 역공" — 뉘앙스 선택.

## 2b. 21바이트 슬롯 초과 위험 (v2.0 인수인계서 기준 확장)

v1.0에서는 SCENARIO_TITLE_005만 슬롯 초과 위험으로 표시되어 있었으나, v2.0
인수인계서 ⅩⅪ-6절은 이 위험을 다음 5개 항목으로 확장했다. 실제 인코딩
전까지는 전부 `UNKNOWN`이며, 아래는 어디를 우선 확인해야 하는지에 대한
힌트일 뿐 결과가 아니다.

- SCENARIO_TITLE_002: "오케하자마 전투"
- SCENARIO_TITLE_003: "노부나가 포위망" (기본안)
- SCENARIO_TITLE_005: "코마키·나가쿠테 전투" (기존부터 위험 표시됨)
- SCENARIO_TITLE_006: "마사무네의 반격"
- SCENARIO_TITLE_007: "세키가하라 전투"

## 3. 순정성 미확정 항목
- FONT.N11, FONT12.N11: `CANDIDATE_PRISTINE` (독립 순정 교차 검증 미완료)
- SCEDA03/04/08/09/10: 보고상 `CONFIRMED_PRISTINE`이나 근거가 "Steam 무결성
  확보"로만 기술되어 세부 확인 필요

## 4. 기존 도구 재검증 필요
- `font_patcher.py`, `custom_encoding.py`, `glyph_renderer.py`,
  `preflight_validator.py` — 모두 이 저장소에 없으므로 존재·동작 여부부터
  확인 필요.

## 5. 자동으로 처리하지 않은 것 (금지 사항 준수)
- 어떤 후보 번역도 `APPROVED`로 표시하지 않음.
- 가운뎃점을 하이픈/공백으로 임의 대체하지 않음.
- 21바이트 초과 여부를 추정치로 판정하지 않음(모두 `UNKNOWN`으로 유지).
- P4로 자동 진입하지 않음.
