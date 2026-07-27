# 《신장의 야망 11 천하창세 PK》 자연 한글패치 — 통합 프로젝트 인수인계서 v2.0

- 작성 기준일: 2026-07-27
- 문서 목적: 이전 대화 확인 없이 즉시 재개하기 위한 단일 공식 기준서
- 참고 설계: `parsifal295/nobu16-korean-patch` v0.15.1 (아키텍처만 참고, 리소스 직접 재사용 금지)
- 현재 공식 단계: Stage P3 (자연 한국어 번역·바이트·글리프 검증)
- 작업 모드: 읽기 전용 / 게임 파일 수정 금지
- 다음 공식 산출물: `P3_READY_FOR_REVIEW_REPORT`

> **본 문서는 `PROJECT_HANDOVER_v1.0.md`를 대체한다.** 향후 변경 사항은 이 파일을
> 직접 고치지 말고 `docs/CHANGELOG.md`에 버전과 변경 이력을 남긴 뒤 새
> `PROJECT_HANDOVER_vX.Y.md`를 추가하는 방식으로 관리한다. 이 문서가
> `walkthrough.md`, `task.md`, 개별 P0~P2 보고서보다 상위 기준이다 — 단, 이
> 저장소에는 그 파일들 자체가 존재하지 않으므로(로컬 Windows PC / Antigravity
> 브레인 폴더에만 존재), "상위 문서" 관계는 자료가 실제로 반입된 이후에만
> 의미를 가진다.

## v1.0 대비 변경점 (실질적 차이만 기록)

- Ⅲ-6 "Fail-Closed" 원칙 명문화: 미등록 해시·알 수 없는 수정본·부분 패치
  상태·백업 불일치 시 무조건 적용 중단.
- Ⅴ에 `CODE_MAP_MODIFICATION: PROHIBITED` 명시적 추가.
- ⅩⅤ에 `capture_ocr_helper.py` 보고된 SHA-256 추가:
  `e34363fdd78b2c37e78ae19e4c3164fbe38db6adeceb7be6f54a24a618ce8e7a`
  (도구 파일 자체는 이 저장소에 없음 — 검증 시 대조용 참고치일 뿐).
- ⅩⅪ-6 "21바이트 슬롯 초과 위험" 목록이 기존 SCENARIO_TITLE_005 단독에서
  다음 5건으로 확장됨: 오케하자마 전투(002), 노부나가 포위망(003 기본안),
  코마키·나가쿠테 전투(005), 마사무네의 반격(006), 세키가하라 전투(007).
  → `work/p3_.../reports/p3_unresolved_items.md`에 반영.
- ⅩⅧ-5에 계산식 명문화: `total_slot_usage = encoded_length + 1`,
  통과 조건 `total_slot_usage <= 21`.
- ⅩⅧ-2에 `BLOCKED_P2_EVIDENCE` 상태명 명시.
- ⅩⅪ-8 OneDrive/한글 경로 인코딩 주의사항 추가 (도구 구현 시 `pathlib.Path`,
  UTF-8 JSON, 상대 경로 권장 — 실제 도구가 이 저장소에 없어 현재는 적용 대상
  없음).
- 나머지 SCEDA/FONT 오프셋·해시·슬롯 규칙·7개 번역 후보 내용은 v1.0과 동일.

## 핵심 요약 (재확인)

- **PATCH_TARGETS**: `scenario/SCEDA01~04,08~10.N11`, `grp/FONT.N11`, `grp/FONT12.N11`
- **PROFILE_IDENTITY_TARGET**: `Nobunaga11WPK.exe` (수정 안 함)
- **SCEDA 제목 슬롯**: offset `0x1AE`, 21바이트, 단일 NUL 종료, NUL 패딩, 뒤 14바이트 메타데이터 절대 변경 금지
- **FONT**: `FONT.N11`(16×16, 4bpp, 128B/glyph), `FONT12.N11`(12×16, 4bpp, 96B/glyph) — 둘 다 `CANDIDATE_PRISTINE`, 독립 순정 교차 검증 미완료
- **금지**: 게임 폴더 수정, SCEDA/FONT 실삽입, EXE/메모리 패치, 코드표 자동 수정, 자동 APPROVED, P4 자동 진입, APPLY/RESTORE, 공개 배포
- **다음 담당자 작업(ⅩⅫ)**: 인수인계 자료 실재 확인 → P2 증거 감사 → P3 격리 작업공간 → 인코더 검증 → 7개 후보 인코딩 → 대체 후보 비교 → 필요 글리프 생성 → 산출물 작성 → 안전 감사 → `READY_FOR_REVIEW`로 중단
