# BASS_HE R10A canonical recovery handoff

이 파일은 PR17의 이전 R10A handoff가 155-byte visibility-error 문자열로 오염된 사건을 복구한 canonical start contract다. 구현/수치 작업은 반드시 이 파일과 byte-restored 원본 `R10A_HANDOFF_KO.md`를 함께 읽고 시작한다.

## 0. Fresh identity gate

Repository: `cosmosapjw-quantum/BASS_HE`

Fresh-read:
- PR15 branch `audit11/dr11h-certificate-binding`
- expected PR15 HEAD `b8b2fe47a367459f6faf6796eb2f251feacbbd7c`
- PR17 branch `research/shared-c64-crossrepo-20260928`
- root `AGENTS.md`

R10 verified archive:
- `BASS_HE_R10_POLICY_RHO_AUDIT_20260929_v1.zip`
- bytes 10029
- SHA256 `9c810208d48c2a89c2ef425d758109f5c4d119c86a52cefdc5da37b139046ee5`
- ZIP CRC PASS
- Drive object `1sAhc_wRuLji0_FDpJEjoMfaoEeFo305h`

Recovered exact Git blobs:
- `R10A_HANDOFF_KO.md` -> `38546ac82ebbd15f70560bd1cc2631537db44ddc`
- `RESEARCH_REPORT_KO.md` -> `bcba7947ec1c03a0bbb6aa1a6f7fd81736d3bcf5`
- `LITERATURE_NOTES.md` -> `23613e7b0415cfa178e9c740b5cf5ea5625a3cdd`
- `CURRENT_STATE.json` -> `3b3932750b9640a4d82d16ab499cc811945b5c2c`
- `MANIFEST.json` -> `c181c75f411d78b8b64bea0b816e9beec9860d5d`

이 blob들이 다르면 중지하고 `R10_CONTRACT_IDENTITY_MISMATCH`를 반환한다. 정상이라면 restored `R10A_HANDOFF_KO.md`의 전체 계약을 authoritative base로 사용한다.

## 1. Frozen gates

그대로 유지:
- `CODE_I02_CLOSED=true`
- `full_certificate_fail_closed=true`
- `scientific_PROMOTE=HOLD`
- `Eq55_next_node_authorized=false`
- `Eq55=NOT_RUN`

R10 policy:
- F2-RHO = primary research candidate
- F2-FROZEN = R9 author `CMES(1)` artifact를 재현하는 research-only lane
- F1-RHO = printed Eq.(52) source-compatibility control
- Appendix-A metric은 `AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`
- production default 변경 금지

## 2. Historical DR8 raw anchors가 없어도 R10A는 BLOCKED가 아님

현재 repo에는 다음 실제 알고리즘이 남아 있다.
- `src/bass_he/eq54.py::DeltaSurrogate`
- `src/bass_he/eq54.py::validate_delta_surrogate`
- `src/bass_he/geometry.py::adaptive_seed_rhos`
- `src/bass_he/geometry.py::adaptive_vector_quadrature`
- `evidence/DR8_ADAPTIVE_SURROGATE_STUDY.json`
- `evidence/DR8V_ADVERSARIAL_HOLDOUT.json`

누락된 것은 historical raw anchor bytes다.

R10 recovery 연구:
- Wolfram은 `sqrt(Rc^2-rho^2)`와 `sqrt(X^2+rho^2)`가 rho에 대해 even임을 확인했다. 고정 analytic branch에서 local expansion은 even powers, 즉 `u=rho^2`로 자연스럽게 조직된다.
- 이것은 u-coordinate의 정당화이지 Delta의 global cubic accuracy 증명이 아니다.
- SciSpace hidden-crossing/advanced-adiabatic 문헌은 impact-parameter dependence가 구조적임을 지지하지만 특정 cubic interpolation을 승인하지 않는다.
따라서 held-out validation은 필수다.

먼저 Git/Drive/Dropbox의 기존 BASS_HE durable artifact에서 raw DR8 anchor table을 찾는다. DR8 evidence identity와 연결되지 않는 transcript-only/rounded table은 사용하지 않는다.

찾지 못하면:
`SURROGATE_SOURCE=FRESH_R10A_REBUILD_NOT_DR8_BYTE_REPRODUCTION`
으로 기록하고 아래 fresh fallback을 수행한다.

## 3. Fresh surrogate fallback

각 5개 scoped branch마다 `Rb=branch.support_cutoff`.

Initial anchors:
- rho=0
- rho=Rb
- `adaptive_seed_rhos([0.0,Rb], rule='gk7')`의 모든 node

동일 branch/depth/panel/tolerance contract로 exact `stueckelberg_delta`를 계산한다. 생성 후 exact float identity 기준으로만 deduplicate한다.

Holdout은 fit에 넣지 않고 다음 fixed fractions에서 exact 계산:
`rho/Rb = 0.125, 0.375, 0.625, 0.875, 0.95, 0.99`

`validate_delta_surrogate`의
`max_relative_error <= 2e-4`
를 요구한다. 이는 published DR8 runtime gate다.

실패 시 branch별 u=rho^2 interval을 한 번만 midpoint split하고 각 child에 gk7 seed node를 추가한 뒤 같은 holdout으로 1회 재검증한다.

그래도 실패하면:
`SURROGATE_REBUILD_UNRESOLVED`
로 중지한다. tolerance 완화, holdout의 training 편입, 다른 interpolation으로 silent switch 금지.

PASS claim ceiling:
`R10A_HELDOUT_NUMERICALLY_VALIDATED_NOT_DR8_BYTE_IDENTICAL_NOT_GLOBAL_BOUND`

## 4. Three-lane calculation

Surrogate admission 뒤에만 restored R10A 계약대로 실행:

- F2-RHO: `P=exp[-2 Delta(rho)/v]`
- F2-FROZEN: branch support 안에서 `P=exp[-2 Delta(0)/v]`
- F1-RHO: `P=exp[-Delta(rho)/v]`

Scope:
- Nmax=3
- existing five published branches
- E=0.5, 5 keV/u
- branch order, support, rotation, matrix topology, upper-shell handling unchanged

F2-FROZEN은 production source를 수정하지 말고 constant-delta geometry mapping으로 기존 batch/integration path에 공급하는 research adapter를 우선한다.

## 5. Required diagnostics

각 branch에서 최소
`rho/Rb = 0, 0.25, 0.5, 0.75, 0.9, 0.99`

기록:
- Delta(rho), Delta(rho)/Delta(0)
- P_F2_RHO, P_F2_FROZEN
- P_F2_FROZEN/P_F2_RHO
- support status

검산식:
`P_F2_FROZEN/P_F2_RHO = exp[-2(Delta0-Delta(rho))/v]`

Wolfram 검산:
`d log P / d Delta = -2/v`

## 6. Integrated comparison

existing support-split adaptive Eq.(54) machinery를 사용한다. historical DR8 call parameter를 추정하지 않는다. 정확한 old parameter가 복구되지 않으면 `NEW_R10A_NUMERICAL_CONTRACT`로 명시하고 실제 사용값을 기록한다.

보고:
- F2-RHO vs F2-FROZEN
- F2-RHO/F2-FROZEN/F1-RHO vs Appendix A
- indexed/shell scoped observables
- componentwise quadrature estimator
- stochasticity/range diagnostics

모든 Appendix-A 비교는:
`AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION`

## 7. Interpretation

A. F2-FROZEN이 Appendix-A를 materially 개선:
R9 `CMES(1)` artifact의 구현-level 영향이 측정됨. F2-FROZEN 물리 승격 금지.

B. 결과는 바뀌지만 author reproduction은 개선 안 됨:
다른 bounded implementation difference가 우세.

C. 차이가 negligible:
이 5 branches/2 energies scope의 empirical upper bound만 보고.

## 8. TDD / non-scope

새 research adapter 전 RED:
- exact frozen probability identity
- lane isolation
- unchanged support/branch order
- analytic probability-ratio identity
- surrogate no-extrapolation + holdout gate

`git diff --check` 실행.

금지:
- CODE-I02 hostile rerun
- production Eq55
- production Eq50/54 default change
- 56-action replay
- worker sweep
- R1/R2
- author FORTRAN execution
- L2/Krawczyk
- tolerance/new channel 변경

full repo pytest는 production/package code를 건드린 경우에만 필요하다.

## 9. Return

새 timestamped PR17 namespace에 append-only 게시하고 다음을 반환:
- PR15/PR17 exact identity
- old raw anchor recovery 여부
- fresh rebuild이면 complete anchor/holdout manifest
- surrogate validation + claim ceiling
- three-lane outputs
- measured R9 I2 impact
- Appendix-A implementation-reproduction metrics
- commands/exit codes
- not-run list
- dual-backup receipt
- bounded next decision prompt

이 execution context에서는 frozen gates를 변경하지 않는다.
