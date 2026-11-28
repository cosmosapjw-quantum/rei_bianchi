# 개발계획 개정 독립 검토

**판정: ACCEPT — 계획 범위 내. 새로운 물리·수치 실행 또는 과학적 채택 판정이 아니다.**

감사 원문, 아래 네 계획 파일, 로컬에 고정된 E13C8/C10 상태·수치 정의, 공통 원자 계약, REI source 확인, BASS N4 보고서와 native polarized Thomson 구현을 읽었다. 외부 변경·검색, 수치 실행, 과거 suite 재실행은 하지 않았다.

## 실질 지적과 반영

초기 F/M/B/B0만으로는 질문에 포함된 전자 이력 민감도를 고정 geometry에서 분리할 수 없었다. 작성자가 B_F/M_F를 추가하여 `[B−M](ne_B)−[B_F−M_F](ne_F)`를 정의했고, 수정된 계획·DAG·handoff를 확인했다. 서로 다른 proper-time 셀 평균을 점밀도로 복사하지 않으며 공통 a/B-clock 재투영과 그 오차를 새 연결 범위에 포함한다. q2의 μ는 공통 tetrad의 LRS 축 기준으로, p_L의 I=0은 정의 불가 mask로 명시됐다. 이 수정으로 검토에서 발견한 계획상의 누락이 닫혔다.

## 채택 근거

- 감사의 우선순위 전환은 채택하되 이미 있던 원자 lane 비차단 원칙, 과거 native 전구간 후보와 최신 C12의 차이를 정정한다. 재검증하지 않은 heating 수치를 새로운 결과로 쓰지 않는다.
- 실제 변경은 BASS_HE의 미래 일정이다. REI/BASS 공동 B1은 제안된 미실행 과제이며 다른 저장소의 코드·실행·채택을 완료했다고 표시하지 않는다.
- E13C8/C9/C10의 scoped finite 결과, C10 full population NOT_RUN 및 E13 계보의 physical/continuum/production/receiver HOLD를 보존한다. 유한 포함 폭과 물리 오차를 구분하며 누적 P/H를 순간 Γ 또는 실제 RCT spectrum으로 export하지 않는다.
- 기존 Liouville·Thomson·N4 adapter를 다시 만드는 과제를 피한다. B1은 실제 collision-depth 전달, matched-H 방향 반응, 산란 제거 대조, history 반응, CSV·그림·해석으로 닫는다. 문서 생성만으로 완료되지 않는다.
- proper density·proper seconds·상수비·무차원 충돌 깊이 및 새 결합의 시간 순서를 다룬다. scalar matched-H 퇴화를 전체 Bianchi no-go로 확대하지 않고 q2/편광 출력을 관측 CMB C_l 또는 total observer τ로 승격하지 않는다.
- paired 10%는 앞으로 확인할 탐색 benchmark 목표다. 이미 검증된 정밀도·엄밀 구간·관측 제약으로 쓰지 않으며, 0 근처 반응은 절대 null/refinement 한계 또는 미해결로 보고한다.
- E13C11은 구체적인 observable 병목 또는 독립 수학 질문이 있을 때 재개한다. 현재 NCP 작업은 0이며 짧은 pilot·새 연결 검사·후처리는 HERE 우선이다. 완료된 과학 계산과 전체 archive 복구를 반복하지 않는다.

## 판정의 한계

이 검토는 실행 가능한 다음 과제를 선정한 계획 검토다. B1의 새 결합은 PLANNED_NOT_RUN이며 실제 transport 정확도, 신호 존재, 관측 식별성은 평가하지 않았다. 두 prescribed history의 대조 자체는 fesc/C/T 전체의 천체물리 불확실성 분석을 대신하지 않는다. 추가 원자 gate나 새 전수 인증을 이 계획의 선행조건으로 만들지 않는다.

## 검토한 파일의 고정 identity

작성 시각(UTC): 2026-10-12T06:28:41.680425+00:00

다음 SHA-256은 이 검토를 작성할 때 읽은 실제 네 파일의 bytes로 계산했다. 이후 과학 내용이 바뀌면 이 판정의 대상도 달라진다.

| 파일 | Bytes | SHA-256 |
|---|---:|---|
| `DEVELOPMENT_PLAN_KO.md` | 26850 | `3f4176a89f33309dece7b564cc2db4c00dee85e4a6f1423b242de210eca86765` |
| `research/scientific_priority_reset_20261012/ACTIVE_DAG.json` | 7705 | `6c0fd9901b847806381ab38a41b8a01c3dec13dd3061257dda8fd87d2591fef0` |
| `research/scientific_priority_reset_20261012/NCP_LOCAL_CODEX_HANDOFF_KO.md` | 6683 | `502f77aa9d32328c7217dda5a14bc19cf6359ee3e49950f861ab5325d85c5063` |
| `research/scientific_priority_reset_20261012/SOURCE_INDEX.json` | 14614 | `1c308c9dbd0ef718040f5930f57e773039c8674210df27dcbf2c26f3aec42f40` |
