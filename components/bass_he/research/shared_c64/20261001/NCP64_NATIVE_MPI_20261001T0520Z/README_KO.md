# NCP64 정확도 보존 최적화 패키지

REPORT_KO.md → HPC_POLICY_KO.md → NEXT_HANDOFF_KO.md 순서로 읽는다.

- reference/: C1b byte-pinned 기준 구현.
- code/: 사전 할당·저메모리 solver, sparse direct operators, native adapter, MPI 작업 실행기·host 검사·성능 sweep.
- native/: Fortran source, strict/debug/native-ISA build, 합성 시험, 초기 느린 버전 보존.
- tests/ 및 evidence/: 실제 비교 결과와 실패 이력. 일부 증거는 runtime 경로를 기록하며 미래 NCP 경로로 간주하지 않는다.
- fixtures/: l96 기준 상태. Git 공개 subset에서는 NPZ를 제외하고 전체 ZIP에 포함한다.

현재 C2 broad-grid 계산은 없으며, actual NCP64 scaling과 core binding은 NOT_RUN/미검증이다. 검증된 현재 범위의 성능·정확도만 REPORT에서 주장한다. 모든 science gate는 parent와 동일하다.
