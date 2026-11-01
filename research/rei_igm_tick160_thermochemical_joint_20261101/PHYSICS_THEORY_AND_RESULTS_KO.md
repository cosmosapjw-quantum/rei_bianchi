# REI central M1 | 원본 tick160 열·화학 결합 closure 및 공통-부모 의존성 진단

**2026-11-01. Source-conditional / derived / numerically checked / scoped implementation verified.**
**Canonical scientific admission: NONE; central 28/88, working 33/88, physical-fast 4/7.**

## 원본 계보와 실제 자료
- `cosmosapjw-quantum/rei_bianchi` PR #320 HEAD `e5836fc4b8804d1bcdcdcbb97ab33f822703fa46` (2026-11-01 readback).
- 원본 8월 29일 source owner archived blocked run commit `a35c8b3fceaf9c832b401bc01480f5e3b0b4af30`, original 35-member TAR SHA256 `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`.
- 원본을 실제로 읽은 GitHub Actions run [41259585168](https://github.com/cosmosapjw-quantum/rei_bianchi/actions/runs/41259585168) artifact #13064333012, 12,591,114 bytes, SHA256 `48ad5c6f0922ad946a10a89ce17fefd2c7241ac956b6bac194892a42810312a7`. 원본 상태 46,080-node, 3개 계산 lane의 **숫자 배열 완전 동일** (`cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01`). 원본 수용 3 endpoint, tick 160/131072; 다음 [160,161] tick에서 세 lane 모두 BLOCKED_MINIMUM_STEP.
- 현재 연구의 입력 ZIP SHA+ZIP CRC 검증과 모든 3 lane 46,080행 완전 일치. 유효한 고유 물리 상태는 46,080개, 138,240개의 독립 시뮬레이션이 아님.

## 정의와 단위
관례 `(-,+,+,+)`; 수소핵당 원자수, `k_B=1.380649e-16 erg/K`, `1 eV=1.602176634e-12 erg`; `c`는 원자 에너지 정의에 끼어들지 않으며 광학깊이/수송은 이번 작업에 포함되지 않음. 원본 source는 정상 3차원 비상대론 단원자 가스 열적 자유도를 사용함.

`x_HII=N_HII/N_H`, `x_HeII=N_HeII/N_He`, `x_HeIII=N_HeIII/N_He`. 원본 전하와 열 관계에서 서로 독립적으로 추론한 `y=N_He/N_H=0.079`. `x_e=x_HII+y(x_HeII+2x_HeIII)`, `n_part/N_H=1+y+x_e`. 실제 소스 midpoint 46,080개에서 서로 독립적으로 계산한 y의 최댓값 절대 편차 `2.65e-9`; 원본 이력의 정확한 fraction은 interval state이므로 midpoint는 편의상 대표값일 뿐 유일한 참값이 아님.

Ionization energies are **new explicit NIST atomic reference constants** rather than claiming the original 26-event code adopted precisely the same constants: H I `13.598434599702 eV`, He I `24.587389011 eV`, He II `54.4177655282 eV`. Source: [NIST ASD](https://physics.nist.gov/asd), DOI `10.18434/T4W30F`. Ionization energy zero is fixed at neutral ground states.

Per H nucleus:

\[
 u_{\rm th}=\frac32 k_B T(1+y+x_e),\qquad
 u_{\rm ion}=I_H x_{\rm HII}+y[I_{\rm HeI}x_{\rm HeII}+(I_{\rm HeI}+I_{\rm HeII})x_{\rm HeIII}],\qquad
 u_{\rm mat}=u_{\rm th}+u_{\rm ion}.
\]

All `u` are energies per H nucleus. `u_mat` is **local H/He gas thermal + atomic binding energy only**, NOT the original owner augmented gas+photon+escaping radiation+gravity ledger; fixed `u_mat` is an isochoric *counterfactual variation* and is NOT a time-dependent conservation law in the full radiation-coupled reionization problem.

## 구성적 유도: 국소 이온화 채널의 열적 민감도
With fixed `u_mat`, set `N=1+y+x_e` and `u_th=u_mat-u_ion`. Then

\[
\log T=\log (u_{\rm mat}-u_{\rm ion})-\log N-\log(3k_B/2).
\]

Therefore for a physical H I -> H II reaction `d x_HII=d\xi_H`,

\[
-\frac{\partial\log T}{\partial\xi_H}\Big|_{u_{\rm mat}}
=\frac{I_H}{u_{\rm th}}+\frac{1}{N}.
\]

For He I -> He II `d x_HeII=d\xi_{He1}`:

\[
-\partial_{\xi_{He1}}\log T=\frac{yI_{\rm HeI}}{u_{\rm th}}+\frac{y}{N}.
\]

For physical He II -> He III `d x_HeII=-d\xi_{He2}`, `d x_HeIII=d\xi_{He2}`:

\[
-\partial_{\xi_{He2}}\log T=\frac{yI_{\rm HeII}}{u_{\rm th}}+\frac{y}{N}.
\]

Compare fixed thermal energy (`du_th=0`), where only the second `1/N` term survives. These are local thermodynamic sensitivities; the real 26-event Jacobian also requires each event rate, photon feedback, full state source correlations and time integrator derivatives. No change to original full/two-half estimator is proposed or accepted.

SymPy-independent Wolfram Language `FullSimplify` of 3 components of `D[Log[T],x] + D[u_ion,x]/u_th + D[N,x]/N` returned `{0,0,0}`; the first attempted script used protected `E,N` symbols and generated warnings, discarded in favor of a clean reevaluation. Python finite differences directly checked the independently coded thermodynamic logarithm on 200 real source nodes.

## 실제 46,080-node 결과 (equal-node percentiles, not volume/mass weighting)

| Quantity | p05 | p50 | p95 |
|---|---:|---:|---:|
| `T_gas [K]` | 2238.569 | 11828.327 | 61937.767 |
| `u_ion [eV/H]` | 15.50723 | 15.54747 | 15.58538 |
| `u_th [eV/H]` | 0.624415 | 3.298727 | 17.285416 |
| Nodewise `u_ion/u_th` | 0.90257 | 4.72272 | 24.89027 |
| \(|\partial_{\xi_H}\ln T|_{u_{mat}}\) | 1.24987 | 4.59823 | 22.24127 |
| \(|\partial_{\xi_{He1}}\ln T|_{u_{mat}}\) | 0.14896 | 0.62722 | 3.14737 |
| \(|\partial_{\xi_{He2}}\ln T|_{u_{mat}}\) | 0.28530 | 1.34378 | 6.92146 |

Source midpoint closure `3/2 k_B T N=u_th` max relative residual `1.2304e-9`. Separate charge-vs-thermal y consistency worst `2.6457e-9`. Original source temperature log interval width maximum `1.72093011e-4`. Reconstructing T from **independent marginal enclosures** for the original U and x_e raises max width to `2.10816672e-4` and the median width ratio to `1.2518297`; 252 nodes' rebuilt widths exceed numeric `2e-4` whereas none of the stored T widths do. **These are width-scale diagnostics, not original local truncation-error pass/fail**. Do not subtract widths from the original one-tick error `2.1245050576368385e-4`.

## 실제 물리적 의의와 admission 한계
A significant fraction of original nodes has atomic binding energy comparable to or much larger than gas thermal energy. A chemistry step perturbs both energy storage and particle count, so an original-source common-parent local-error bound should retain shared `u`, ion fractions, source and Hummer-Seaton rate correlations. This provides concrete magnitude and signs for the **thermochemical closure component** of a future 26-event joint sensitivity implementation, not a time-domain result for its full integrator.

**Unresolved:** The original 26-event numerical map `D_h(X,theta)` was NOT recalculated at [160,161]. The full first canonical FLRW interval still fails its original strict local-error condition. Independent external distinct-author referee NOT_RUN, native subagents NOT_RUN, cosmological Bianchi/RT observables NOT_RUN, PR merge NO. Central 28/88, working 33/88, fast 4/7, delta 0.

## Reproduction
Download exact PR320 source artifact #13064333012 (`REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip`), then run:

```
python code/thermochemical_closure.py --input inputs/REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip --output outputs
REI_INPUT_ARCHIVE=inputs/REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip python -m unittest discover -s tests -v
python code/independent_audit.py --source-archive inputs/REI_PR320_ORIGINAL_TICK160_PHYSICS_20261101.zip --candidate outputs/ORIGINAL_TICK160_46080_THERMOCHEMICAL_CLOSURE.csv.gz --output outputs/INDEPENDENT_AUDIT.json
```

Full source-inclusive ZIP includes the CI artifact as bytes, full 46,080-row gzip CSV, four figures, code, tests, result checksums and this report. Git Draft PR includes code, source reference, 12 source-backed numerical witness rows and compact scientific summary, **not** original binary or full CSV. No dual-provider remote readback asserted.
