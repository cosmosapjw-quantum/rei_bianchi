# REI age-exposure/source-age 현재 상태 | 2026-10-19 (block-max 실행 후)

진입 문서는 이 파일, `RESEARCH_UPDATE_20261019_BLOCKMAX_KO.md`, `contracts/NEXT_DAG_CURRENT.json`, `DELIVERY_RECEIPT_CURRENT.json`이다. 이전 단계 기록은 `RESEARCH_UPDATE_20261019_KO.md`와 `evidence/current_entries_before_blockmax_20261019/`에 그대로 있다. PR199는 draft다. intake HEAD `18aae24bd1d102c50164bd6224a09ec5c4eaf45d`, 과학 코드 `db87456e6b2b528a046f7856c04c73c7b4b43a54`, original physics `35d9747a0bbedcafdb568467ce7c1e7a25f965b6`.

## 완료된 실제 결과

- **q0 age64 block-max (새, NCP):** 명령 exit0, 19756 RHS, case wall 782.731 s, 48 transport threads, binary64. 고정 gate 유지 상태에서 photon `2.002711130429069e-10 ≤ 1e-8`, energy `1.93e-13`. 정확한 유리수 재합산도 PASS. 단일 사례 결과이며 재실행하지 않는다.
- **해석:** 기존 RMS 대비 photon 잔차 0.0199배. 그러나 block-max는 정의상 더 엄격하고 step 수도 늘었으므로(후반 11→16) RMS 희석과 일반적 step 축소를 **판별하지 않는다**. 독립 검토 `evidence/independent_review_blockmax_20261019/REVIEW.json`.
- charge/species residual은 저장값이며 assert가 없다. 18개 관측 기록은 9개 고유 상태다. source-jump paired snapshot은 MISSING_DATA다. DR은 aggregate 0이다.
- **age 수렴성 HOLD:** 같은 source의 age32 reference가 없다. PR171 age32는 controller/solver/binary가 달라 비교하지 않았다.
- spectral128 완료(He I 64→128 0.2660778682%), 기존 RMS age64 실패(1.0081783527976493e-8), native time8 subnormal 진단과 count 교정 후 energy 2η>η 실패는 모두 이전 그대로다. native time16/32는 HOLD다.

## 현재 NCP READY

**없음.** 다음 후보는 모두 로컬 구현·테스트·검토가 먼저 필요하다.

1. `R_BLOCK_MAX_BINDING_BLOCK_LOG`: accepted step마다 E_block을 결정한 block 기록(수치 변경 없음).
2. `R_AGE32_BLOCK_MAX_SAME_SOURCE`: runner plan에 age32 reference 항목 추가 후 단일 실행.
3. `R_SOURCE_JUMP_PAIRED_SNAPSHOTS`: birth-jump 측 검사 계측.
4. `R_NATIVE_COUNT_ENERGY_STORAGE`: THEORY_REQUIRED.

미해결 수치 질문: native가 구간 끝점 trial state를 `IGM_STATE_OR_UNIT_DOMAIN`으로 거부하고 `max_step=Δ/4`로 재시작하는 패턴(65구간 중 60, 두 controller 공통).

owner checkout, PR150/R9, 별도 BASS HHeD lane은 변경하지 않았다. **`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`**.
