# IGM blocker 후속 구현 (draft PR89)

실제 BASS/REC 연결, joint rate export, canonical owner/checkpoint 경로와 scalar-underflow 이후의 tracked photon transport를 구현했다. source/provider/closure/허용오차와 IGM 기본 OFF는 변경하지 않았다. PR85 log-tail, PR86 canonical Wide, PR86/88 저장 source도 교체하지 않았다.

수치 후속은 완료된 prefix를 재실행하지 않고 coarse k16, fine k28, tail k14에서 재개했다. `Tracked/Wide` N/U pair와 독립 energy loss를 characteristic 내부 모든 segment로 전달하고, V3 endpoint energy discrepancy를 U/red/B loss로 보존했다. accepted-record replay는 durable scalar 순서와 canonical ledger 순서의 명시적 순열을 사용하며 실제 2-transition capture/replay를 통과했다.

최종 0.0008 horizon은 coarse k48, fine k96, tail k48, `ln(a)=-2.564149357461537`, `z=11.98960415889089`에 도달했다. 저장된 32개 공통 시각의 원 37-field 비교는 temporal 최대 허용비 `0.023932797389989293`, tail `4.080871757717751e-12`; source N/E 최대 허용비 `0.21071655885039875`로 통과했다. 이 결과는 `MANUFACTURED_MODEL_DISCRETE_REFINEMENT_PASS`의 0.0008 horizon 범위만 승인한다.

z=12→10의 이후 horizon, 연속 spectral/source/time/Jacobian 오차, historical-prefix 및 kernel/provider 권위, joint nonlinear remainder는 아직 미완이다. `MANUFACTURED_MODEL_CONTINUUM_VALIDATED`와 physical claim은 HOLD다. REC Gate I·matched evolution은 HOLD, BASS 유한 창 밖 optical depth는 UNKNOWN이다.

재현과 증거:

```sh
python3 research/igm_handoff_20261008/scripts/verify_package.py
python3 research/igm_handoff_20261008/scripts/reproduce.py --output /tmp/igm-handoff
python3 research/igm_rate_export01_20261008/reproduce.py --output /tmp/igm-rate
python3 research/igm_blockers_20261008/bass/verify.py --output /tmp/igm-bass
python3 -m unittest discover -s research/igm_blockers_20261008/rec -p 'test_*.py' -v
cargo test --manifest-path research/igm_blockers_20261008/numeric/source/rei-next-nodes/short-hhe-midpoint/Cargo.toml --locked
python3 research/igm_blockers_20261008/repair_20261008/compare_common_48.py
```

실제 명령·exit·observer/provider 비용·실패 보존·독립 리뷰·남은 blocker는 `TASK_RETURN.json`과 `repair_20261008/`에 기록했다. PR89는 draft로 유지하며 merge하지 않는다.
