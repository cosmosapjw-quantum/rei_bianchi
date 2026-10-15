# FLRW production 통합 — 2026-10-15

첫 목표는 Rust cold H/He FLRW 이력의 실제 물리 표현을 개선하고, abundance·Tgas·경과 proper time을 신뢰할 수 있는 조건부 결과로 만드는 것이다. 최신 사용자 지시는 production 코드 수정·통제된 실행과 여섯 저장소 원전 통합을 허용한다. 과거 SCENARIO_LOCK과 영수증은 그대로 보존한다.

현재 단위는 native GL8 finite-interval clock, 공유 geometry, 명시적인 baseline/donor IC를 연결하는 것이다. native clock/driver targeted 21 tests는 raw/targeted_tests_receipt.json의 returncode=0으로 scoped PASS다. baseline/donor 각 2 accepted-step native probe도 scoped PASS다. 독립 심사는 **PASS_SCOPED_CHANGED_SEAMS**다 (INDEPENDENT_REVIEW.json). z19.99 cfg pilot·전체 history·scaling 완료를 뜻하지 않는다. 이 문서의 구성식·upstream receipt는 이번 native 실행의 PASS가 아니다. 기존 ZERO z20→4 312237 accepted-step 조건부 결과는 변경 없이 재사용하며 전체 history를 반복하지 않는다.

**가장 중요한 다음 작업:** 반복 fixed-energy 투영 뒤 grid 에너지에서 문턱을 평가하면 허위 HeII 사건이 생기는 알려진 표현 결함을 해결한다. 기존 driver에도 characteristic pullback은 있다. 에너지 이동 자체가 없는 문제가 아니며 clock 수정으로 치유되지 않는다. 다음 native 단위는 covariant invariant 또는 birth-cohort transport와 기존 coupled cold chemistry의 연결이다. 이어 positive source subcell quadrature·실제 child N/U·age/ray/clock 영수증을 결속한다. 전체 production admission은 표현 수정과 refinement를 기다린다.

읽기 순서: `HANDOFF.json` → `NEXT_DAG.json` → `THEORY_CLOCK.md` → 필요한 `evidence/*_intake.md` 한 개 → 해당 `TASK_PACKETS.jsonl` 항목. `CODEX_HANDOFF_KO.md`는 다음 세션용 복사 프롬프트다. `PR_PLAN.md`는 공개 범위, `POLICY_DELTA.md`는 현재 승인과 과학적 주장 범위를 구분한다.

`configs/hyrec_donor_pilot.cfg`는 z20→19.99의 유한 조건부 수치실험이다. `hyrec_donor_full.cfg`는 미래 NCP 실행 구성일 뿐 여기서 시작하지 않는다. source 변경 뒤에는 항상 fresh output을 쓴다. donor는 REC PR94 xe/T를 recipient nH/fHe에 투영한 조건부 IC이며 독립 species-resolved helium 또는 전체 BBN inventory가 아니다.

Cold Grackle 1–10^6 K 모델은 유지한다. HH의 thermal k_HH(T)는 실제 누락된 물리 입력이고 승인을 기다리는 항목이 아니다. CR-on은 선택 source와 thermal/active electron·cutoff energy/count 결속이 필요하며 CR-off FLRW를 막지 않는다. BASS Einstein/massive/Stokes는 필요한 모델이 선택될 때 별도 연결한다. 추가 D/H charge-exchange는 독립 standalone 단위로 진행하고 HHe 완료를 기다리게 하지 않는다.

실제 tiny probe는 IC별 comparisons20, attempts60, rejects18, RHS444와 checkpoint roundtrip=true를 기록했다. |number residual|≤2.27e−26, |energy residual|≤4.34e−19 eV/H이며 source/probe readback은 일치했다. raw/native_probe_receipt.json 및 두 IC summary를 재사용한다.

실제 probe의 scale-factor 증가는 약3.63e−11뿐이다. 두 accepted steps 전 각각18회 rejection이 있었으므로 전체 history 실행 가능성이나 scaling을 주장하지 않는다. 상세 R/C 상태는 LOOP_STATUS.json과 CODING_LOOP.md를 읽는다.

D/H standalone native kernel도 실제7 targeted tests를 통과했다. 전체 changed targeted tests는28개이며 독립 심사·최종 공개는 아직 대기다.
