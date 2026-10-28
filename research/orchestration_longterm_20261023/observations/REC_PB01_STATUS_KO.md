# REC-HISTORY-PB01 — immutable science S2 관측

과학 판정: `PASS_SCOPED_ENDPOINT_QUERY_PULLBACK_AFTER_SAVED_EVENT_PAIRING_REPAIR`.

이 관측은 과학 S2의18/20 snapshot이다. R10/C10 실제 최종 전달20/20은 후속 REC S3·compact companion에서 별도로 기록한다. 새 중앙 commit 자신의 SHA/ACK를 이 준비물에 미리 기록하지 않는다.

실제 REC source: `f9051f10f02582d6b339d8738f1e9796953941d4`, draft PR137, `research/rec_history_pullback_20261025`.

## 실제 결과

원본 query313개, prefix5127, distinct endpoint626개에 결속한 anchored native chart, A=Ks P, C=Ks diag(g), coordinate adjoint와 exact mixed remainder를 완료했다.
Endpoint norm interval: [1.17562722922718, 1.1756272292401908]; query norm interval: [6.289216981912579e-13, 6.28921698191771e-13].
원 primary exit2와 FAILED raw381개는 보존했다. Saved32vectors의 shared-event sign repair로 첫4성분을 그대로 유지했으며 patched primary는 재실행하지 않았다.

## 실제 S2 전달

파일 `REC_HISTORY_PB01_S2_20261025_b43ec958374b.zip`, 69336495bytes, SHA256 `b43ec958374bb8ba97073c46355dc26131a64261cd5004fa64e65c6565da00d1`.
Dropbox `id:BSpOijBcT10AAAAAAD_-Dw`, rev `65ea5beccbee90af03d47`; Drive `1eHZ_wuG_4J_mgDrBvtRGe2QBpx_kpCAw`. 양쪽 actual ACK size가 일치한다.
Outer remote whole SHA/CRC와712payload 검증 PASS는 REC delivery/S2_REMOTE_READBACK.json에 별도로 기록했다. 내부 과거 KS01/THERMO 과학을 재실행하거나 재검증하지 않았다.

Controlled CPU4.237821s / wall4.424445926001681s. Independent measured readback CPU0.035253s는 별도이며 알려진 CPU subset4.273074s, inherited 포함36.442061486s이다. 미측정 wrapper/I/O/fullturn/remote CAS는0으로 처리하지 않는다.

## 유지되는 범위

Parent REC-HISTORY=PARTIAL; H5=INPUT_DEPENDENT_UNCALIBRATED; physical epsilon/reference/endpoint/curvature/absolute-history/outgoing bounds는null.
H6 actual trace/frame/measure/clock/source/query owner와 physical DY/DQ/Dtheta/reference/geometry/thermal composition은OPEN. Physical HOLD, REC_U5 HOLD_9_FAIL/HOLD_8_FAIL, CLOSED_HOLD_NOT_RESET, global_convergence NOT_RUN, production NOT_APPROVED, REI_activation=false를 유지한다.

Captured publication base `b24a9daee54fc0860c4cf299c4ea5f2a977c0fd4`의 latest 다른38node와 HE/CR/HH 관측을 보존한다. Prior REC18fields와 원return6개를 그대로 이월하고 REC-HISTORY.observations.PB01만 추가한다. Canonical overwrite·assembler·renderer·merge·activation은 수행하지 않는다.
