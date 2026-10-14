# 늦게 수신한 FLRW06 native 실행 blocker 해소

`8fd440a2e547a61d14d7a890147f7e835fae4f2b`의 준비된 FLRW06을 실제 Rust로 실행했다. 결과는 **NATIVE_EVENT_PHOTON_POINTWISE_REGRESSION_PASS**, 독립 검토·원 연구 스레드 수신 ACK는 후속이다.

- actual source pin: `b553698a114fbff05640ab6ecb95d260410de492`; 지정된 Git blob 6개를 컴파일 전 확인했다.
- compiler: rustc 1.94.1. Compile 1회/실행 process 1회, 각각 exit 0.
- photo valid 11개·invalid 6개와 native event→photon ledger 1개, 총 18 output records.
- scalar 167개 비교, 최대 상대 차 `3.777652226439761e-15`; 고정 기준 `3e-12` 통과.
- 6개 invalid case의 정확한 error code 일치. Expected zero는 tolerance 0 그대로다.
- photon residual `7.703719777548943e-34`, scale `5.752402908695334e-18`; scaled residual 약 `1.3392e-16`으로 고정 `5e-14`를 만족한다.

Drive 원 ZIP은 73,574 bytes/50 entries/SHA256 `0796a9749156cce3f1ee26e204a367bd96802672c7ff32ba1c4edd9b311efeca`를 확인했다. 내부 payload 49개를 실행 전후 모두 검증했고 원래의 compiler-blocked receipt도 보존했다.

원 runner는 기존 전체 Git checkout에서 `git show`로 6개 파일을 읽는다. 이 작업은 이미 원문 바이트를 보관한 workspace이므로 **별도 acquisition adapter**에서 `--source-dir`를 받고 같은 6개 Git blob을 검증했다. 원 runner를 보존하고 수정 diff를 남겼다. Git SHA나 checkout을 꾸미지 않았다. Scientific module 5개, 원 lib의 공통 type 정의, prepared Rust driver, 입력, 80자리 reference, comparator와 tolerance는 변경하지 않았다. 실제 compiled binary도 보존했다.

`PhotonInput.absorption`은 native bin0/1/2의 `homogeneous_photo_rates` 사건율 반환 합으로만 계산된다. Python expected sink를 실행 입력으로 주지 않았다. Prepared driver는 실제 컴파일과 실행으로 처음 확인되었으며 code repair는 필요 없었다.

재현 명령:

```bash
PATH=/tmp/rec_rust_1941/bin:$PATH python research_sync_20261005/late_flrw06/run_native_from_verified_source.py \
  --source-dir research_sync_20261005/source_rei \
  --output /path/to/new-result-directory
```

`RETURN.json`, `EXECUTION_CONTRACT.json`, `ARCHIVE_AND_SOURCE_VERIFICATION.json`, `RUNNER_ADAPTER.diff`와 `native_result/`가 실제 증거다. `supplier/`는 봉인 원본이고 어떤 과거 실패도 이 결과로 덮어쓰지 않았다.

이 결과는 minimal original-module pointwise 회귀다. Full-crate integration, 독립 U 소비기, coupled accepted-stage history, physical/interval admission, F05/F08 완료는 주장하지 않는다. 과거 suite, history, 80자리 reference 계산과 moment-cone 연구를 반복하지 않았다. 다음 단계는 이 actual return의 owner 수신과 명시적 후속 범위 결정이며, 자동 FLRW07 승격은 없다.
