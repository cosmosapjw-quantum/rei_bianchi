# RUN10 승인된 단일 수정·표적 검증 — 2026-10-18 KST

사용자의 “직접 수정·표적 검증 진행” 응답에 따라 coordinator가 한 번의 수정과 한 번의 compile/test 순서를 실행했다. 작업자 사용량 제한을 다른 경로로 우회하지 않았다. 이는 AGENTS.md:118의 명시적 예외이며 지속적인 직접 구현 권한이 아니다.

## 실제 변경과 결과

`spectral_edge_support.rs`의 Simpson 분할 목록에 2048,4096만 추가했다. 기존 `5e-13 * M0` 종료 기준, 물리 상수, 테스트, 모멘트 및 원자 데이터는 그대로다. 소스 SHA256은 `4d5ec3f01f43a07ae4b344ba5923a091f13a189033edaae58bb775de400ecea3`에서 `1c2783125cccb79b353a9e834a6a40eab0c3d8d06777768c844bb3a1dbd50c68`로 바뀌었다.

- `rustc --edition=2024 --test ...`: exit0, 0.924036729 s, peak RSS130174976 bytes.
- 새 private binary의 `--test-threads=1`: exit0, 0.015035328 s, 기존6tests 모두 통과.
- combined0.939175532 s <20 s. 기존 실패 실행3.083172176 s와 진단0.053250708 s를 포함한 누적4.075598416 s.
- 이전4PASS/2MomentConvergenceFAIL은 `../run10_compile_001/`의 원본 소스·로그에 보존했다. 재시도/두 번째 수정은 없었다.

## 주장 범위와 다음 단계

판정은 `PASS_EXISTING_SIX_TESTS_ONLY`. 새 과학적 승인 `NOT_ISSUED`. 독립 검토가 실행됐다고 주장하지 않는다. 실제 coupled BASS 통합, 고정된 회귀 구간 밖의 모멘트 수렴, 전구간 물리 정확도, cold EoR 지원 및 isotope-specific D cross section은 이 테스트가 입증하지 않는다. 기존 H-equality D 근사와 HOLD를 유지한다. CI가 green이라고 주장하지 않는다.

다음에는 이 결과를 재사용하고 RUN10 edge-support의 native source/transport 입력·소유권을 연결해야 한다. 이미 완료된6tests를 다시 실행하지 않는다. 이번 승인은 추가 solver/closure 변경이나 물리 campaign을 허가하지 않는다. 기존 NCP process 상태UNKNOWN, 원 campaign deadline 및 누적 비용은 변경하지 않았다.

## 재개

`python -m json.tool research/external_update_intake_20261016_001/full_inventory_001/resume_20261018/NEXT_READY.json`

`EXECUTION_FREEZE.json`, `OBSERVED_DIFF.patch`, `EXECUTION.json`, raw stdout/stderr가 실제 명령·source/config·exit·wall·CPU·RSS 증거다. Binary는 `/home/cosmosapjw/REI_PRIVATE_SOURCE012_INPUTS_20261016/resume_20261018/run10_repair_001/`에 있으며 Git에 넣지 않는다. `GOAL_DONE=false`, checkpoint `PAUSED_RESUMABLE`.
