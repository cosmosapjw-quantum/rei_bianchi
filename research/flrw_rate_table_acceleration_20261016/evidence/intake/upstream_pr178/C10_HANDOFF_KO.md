# C10 차기 실행계약: Source-consistent production opt-in (not yet authorized scientifically)

직접 소스/계산 기준 PR #150 frozen `6ea2b1b4b3875c9163cafc45efe720afded43fc4`, source blob 4건은 `contracts/C9_RESULTS.json` 참조. Runtime은 원래 Direct(default) 그대로다.

최소 native 수용 작업: 별도 task-owned working directory에서 동일 gas states, photon source history, `X=ln(a/a0)`→proper seconds adapter, 물리 input sha를 유지한다. (1) Direct/PreparedDirect/Table 각각 RHS/현지 에너지 장부, stale-temp EOS invalidation, CI floor and RR/DR fallback을 확인; (2) same physics source의 source-free/source-on paired Jacobian derivatives를 Newton finite differencing 또는 명시적 AD와 비교; (3) 2개 실제 시험 부하에서 temperature query count/distribution, worker count, build cost, RSS, temperature-domain rejections 측정; (4) first accepted-step pair error과 fail-closed reject semantics 확인. 기존 1e-5 coefficient sampled threshold는 변경 금지. 그 자체는 전체 물리 trajectory의 numerical accuracy gate가 아니다.

관측량이 필요하지 않은 이 작은 opt-in 성능경로가 full EoR claim 또는 성능 개선의 입증을 요구하지는 않는다. C9도 원래 source의 테스트 외에 input/oracle retrieval을 반복하지 않는다.

실행(전체 복원 ZIP): `bash scripts/REPLAY_C9_C10.sh`. cargo.lock, source ZIP, SHA identity, test raw가 필요하다. 복원 후 조정이 필요하면 성공 전 결과를 덮어쓰지 말고 새 evidence 파일을 남긴다. 전자, 핵종, 에너지 장부 보존과 native actor decision은 독립 게이트다.
