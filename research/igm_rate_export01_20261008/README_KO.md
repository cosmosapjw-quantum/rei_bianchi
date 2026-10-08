# IGM 후속 — PR87·88 포함

PR87 핸드오프에 PR88의 이미 완료된 순간 six-moment exporter 및 typed singleton receiver를 byte 변경 없이 추가했다. 원 `research/igm_handoff_20261008/`는 그대로 보존한다. 실제 accepted `committed-2` endpoint의 Gamma/incident Ecal, source/provider/threshold/epoch/gas/grid identity는 `../igm_rate_export_receiver_20261008/observed/EXPORT01.json`에 있다. 순간율 생산은 PR88 완료 증거를 재사용하며 native observer를 중복 실행하지 않는다.

새 `adapter.py`는 공개 저장 packet을 그대로 받아 pinned PR88→PR87 typed receiver를 호출한다. private ZIP 없이 실행 가능하며, 원 upstream의 private archive 보존 검사는 변경하지 않는다. packet이 없거나 Gamma/incident energy가 없으면 `MISSING_INSTANTANEOUS_JOINT_MOMENTS`와 producer 필요 필드를 반환한다. 적분 A/B/dt, opacity, nonphoto RHS의 0을 변환하지 않는다. caller는 `readout(packet, expected_context=...)`로 정확한 수신 context를 요구할 수 있다. 이 API는 PR88의 한 고정 observed point만 받는다. 새로운 family 또는 다른 epoch/producer는 별도 producer 계약이 필요하다.

```bash
python3 research/igm_rate_export01_20261008/reproduce.py --output /tmp/igm-followup-new
python3 research/igm_rate_export01_20261008/adapter.py --packet research/igm_rate_export_receiver_20261008/observed/EXPORT01.json --output /tmp/igm-point-new
python3 research/igm_rate_export01_20261008/adapter.py --output /tmp/igm-missing-new
```

첫 두 명령은 exit0, 마지막은 missing 상태를 저장하고 exit2로 거절한다. output은 새 경로여야 한다. 저장 2440행의 여섯 ordered binary64 sum과 typed 출력 parity만 확인한다. 이는 새 spectral/provider 계산이나 참오차 검증이 아니다. 추가 observer/provider/RHS/history 비용은 0이며 기존 PR88 비용은 별도로 유지한다.

`consumers/`는 BASS observable 및 REC 초기조건 schema-only 작업이다. PR88의 한 endpoint만으로 normal-time history나 matched REC radiation을 만들지 않는다. 실제 입력은 NOT_PROVIDED, physical HOLD다. 서로 다른 REI/BASS Thomson 상수 값은 caller가 authority와 함께 명시한다.

HE E6, HH ENERGY03, REI BRIDGE11 최신 반환은 `evidence/intake/`로 읽었으며 중복 실행하지 않았다. HE 세 Gamma 예산은 이 cold-state 여섯 moment와 다르고, HH remap conservation은 rate 정확도를 인증하지 않으며 origin gas clock/direction은 자동 추론하지 않는다. BRIDGE11 discrete order는 연속오차를 인증하지 않는다. CR R12도 full state/EOS와 Tdot particle dilution을 구분하며 total RHS/참오차는 열려 있다.

독립 리뷰와 실행/반환 요약은 `evidence/INDEPENDENT_REVIEW.md`, `VALIDATION_MATRIX.md`, `TASK_RETURN.json`을 따른다. IGM default OFF, source/closure/tolerance, 과거 long-history37-field 8실패 및 short work_E RED, physical/full-Wide/history HOLD를 유지한다. merge하지 않는다.
