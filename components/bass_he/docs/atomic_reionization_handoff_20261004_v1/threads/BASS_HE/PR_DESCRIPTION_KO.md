## 2026-10-04 external-atomic fastest track handoff

재이온화 소비자가 자체 원자 산란의 완결을 기다리는 의존성을 줄이기 위해, 기존 B3 원자 rate/count 공급기와 장기 원자 연구를 연결하는 선행 연구·실행 계획을 추가한다. 기존 연구 branch와 미완료 gate를 유지한다.

이번 추가물은 `docs/atomic_reionization_handoff_20261004_v1/threads/BASS_HE/`다. 원자 code/과학 결과를 덮어쓰지 않으며, 다음 구현의 대상 경로와 수락조건을 명시한다.

- 최신 B5C2 상태와 원계획을 다시 읽고, 원 plans/DAG/registry/gates/handoff/API 자료25개를 origin commit 또는 archive SHA와 함께 byte 그대로 보존했다.
- 기존 B3에 GM25/W82=1.70e-13 cm3/s가 이미 있음을 확인했다. KF96=1e-14와17배 차이를 unresolved로 유지하고 explicit source family 및 common-domain sensitivity를 설계했다. 새 API를 처음부터 만들지 않는다.
- reaction vector, direct electron count, chemical/photon/thermal energy ownership, coupled H/He OTS, energy-per-u→COM 및 Maxwell 평균 범위를 유도했다. Source rate alone cannot determine a photon spectrum or heat moment.
- 정확 산술 검산과 JSON/복사본 해시 검사는 실제 수행했다. 새 molecular solve, thermal integration, B3/rei integration, cosmological history는 실행하지 않았다.
- HE-F1/F2가 source/receiver 준비를 맡고, REI-F09가 공통 paired sensitivity를 한 번 실행한다. HE-F3는 결과 수락만 맡는다. HE-F2 미완료는 명시적 scope의 REI-F08 baseline을 막지 않는다.

기존 `scientific_PROMOTE=HOLD`, `EOR_THEORY_GATE=NOT_SATISFIED`, `Eq55=NOT_RUN`, `physical_source_admission=false`는 유지한다. B5C3/fast-ion/coherent 확장은 LEGACY_LANE.json의 trigger로 개별 재개한다. 이번 게시의 actual commit/tree와 Drive/Dropbox 완료 상태는 detached publication receipt에 기록한다.

이 내용은 현재 draft PR #17의 기존 설명을 보존한 채 추가할 섹션이다. PR merge나 production default 변경을 요청하지 않는다.
