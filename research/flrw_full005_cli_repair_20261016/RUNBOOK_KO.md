# 실제 full005 완료 뒤 CLI 후처리 복구

최신 실제 evidence는 `evidence/FINAL_STATUS.json`이다. source005 Q512는 2026-10-15 21:25:27.916253 UTC, Q1024는 22:28:24.534569 UTC에 각각 zbar=4.0으로 완료됐다. accepted step은 442146과 262660이다. 두 returncode는 0이며 native completion proof가 있다. 과거 z≈12 실행 중 snapshot보다 이 완료 evidence가 최신이다.

기존 AUTO001의 bind는 성공했지만 render는 `UnboundLocalError`로 실패했다. `main()`의 bind 분기에서 쓰인 지역 변수 `run`이 전역 `run()`을 가렸다. 이번 수정은 그 지역 이름을 `run_dir`로 바꾸는 한정 수정이다. 세 집중 CLI 테스트는 통과했다. 새 독립 검토도 scoped PASS이며 `IMPLEMENTATION.json`과 `raw/cli_test.log`로 실제 결과를 확인한다. 이 테스트는 실제 원자료 그림이나 과학적 승인을 뜻하지 않는다.

현재 환경에는 전체 history/abundance/ledger 원자료가 없다. native 원자료 수집 archive의 위치·크기·해시는 `RECOVERY_INVENTORY.json`과 `evidence/COLLECTION_RECEIPT.json`을 따른다. 작은 evidence ZIP이 전체 원자료 백업이라고 주장하지 않는다. native 원자료와 기존 campaign은 이미 있으므로 새 solver trajectory를 시작할 이유가 없다.

독립 검토를 통과한 수정 renderer와 기존 기본 의존성이 들어 있는 최신 배포본을 native NCP checkout에서 사용한다. 기존 campaign `/root/REI_FLRW_COVARIANT_20261015_005/full_campaign001`을 보존하고, 캠페인 바깥의 사용하지 않은 출력 경로를 고른다. NumPy·Matplotlib의 기존 환경을 사용하며 아래 wrapper가 현재 실제 terminal/binding/원자료를 다시 확인한다.

```bash
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py check
python3 research/ncp_direct_resume_20261016/postprocess_ncp.py render \
  --output /root/REI_FLRW_FULL005_DIRECT_POSTPROCESS_20261016_CLI_REPAIR_001
```

위 출력 경로가 이미 있으면 그것을 덮어쓰지 말고 새 경로를 정한다. bind+render 전체 한도는 300초, address space는 8 GiB다. 원래 후처리 절대마감 **2026-10-16 03:50:17.774070 UTC (12:50:17.774070 KST)**를 유지한다. 최초 campaign epoch와 native 12시간 예산은 재설정하지 않는다. 마감 초과·오류는 그 상태와 로그를 보존하고 자동 재시도하지 않는다. 별도 예산이 필요하면 기존 campaign의 연장이 아닌 별도 유한 작업으로 결정한다.

그림은 zbar20 이후 경과 proper time와 실제 저장 Tgas에 대한 H/He 분율만 다룬다. Tgas 축도 시간 순서를 유지한다. D cosmological chemistry는 활성화되지 않았고 D 곡선을 만들지 않는다. Q512/Q1024 pair 차이는 진단값이다. 이것으로 whole-history time/angular convergence나 수치 오차 상한을 주장하지 않는다. 실제 그림·receipt를 독립 검토하기 전 scientific admission은 없다.

완료된 post-cache profile은 build/run allowance 0/0, 완료된 source006은 test/build/run allowance 0/0/0이다. 그 결과를 재사용한다. 이번 후처리에 source006 재빌드·새 trajectory·source005 재시작을 섞지 않는다. 실제 후처리 결과와 native raw archive는 기존 백업 도구로 보존하고, 승인된 저장소의 실제 업로드/readback을 확인한 뒤에만 백업 완료라고 기록한다.
