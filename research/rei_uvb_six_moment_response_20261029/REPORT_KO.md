# REI UVB six-moment source-response 연구 결과 · 2026-10-29

## 선택한 새 단위

PR260의 조건부 GLS coefficient confidence union을 Puchwein2019 fiducial H I/He I/He II 광이온화·광가열 여섯 모멘트에 연결했다. 고정 template spectral shape의 공통 `10^[beta+kappa(z-3.6)]` 스케일링을 사용한다. 이는 H I Lyα 자료에서 보정된 *조건부 source rate*이며 실제 Bianchi 광학깊이·관측량의 반응이나 H/He 독립 보정이 아니다. 물리적 상태·밀도·시계 공급이 없어 새로운 IVP를 수행하지 않았다.

## 실제 원자료 결속

- BB13 seven-row source SHA256 `13b56a066a81f2be6e1a7835275de509fa56bdf48c6eba3400318a4b60c36b7b`: local archived bytes matched exactly.
- Puchwein2019 PR251 Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`의 59행 중 연속13행을 별도 numeric projection으로 보존. Projection SHA256 `dcd13144072584085f49698e40c9822e074fecc2a6046605dc9d67cfe7cc3eff`; original 59-row raw-byte identity는 주장하지 않음.
- 13-knot log-positive HI interpolation vs PR257 frozen seven-point template: maximum `1.1587952819525071e-15` dex.
- PR260 source HEAD `7438e2e85e8f0ecb03292558280521bbf58e707d`; BASS PR234 tau row HEAD `c74317ce5df34c442514eccf8a1e87494657393d`. No branch merge or owner mutation.

## 새 물리·수학 결과

`R_X(z;a)=R_X^P(z)*10^(t^T a)`, `t=(1,z-3.6)`, `a=(beta,kappa)`. `D_a R_X=(ln10) R_X t`, `D_a^2 R_X=(ln10)^2 R_X t t^T`. For `U_q=c+G[-1,1]^8+E_q`, log-factor support `t^T c ± (||G^Tt||_1+sqrt(q*t^TVt))`; exponentiating gives exact conditional **pointwise** six-moment bounds. Different redshift extrema do not imply independent draws. `q1` is a preselected scalar 95% guarantee, `q2` a joint2 coefficient 95% guarantee under the inherited known-C Gaussian assumptions. All physical source-model uncertainties beyond those inputs remain unresolved.

At z=3.6, original Puchwein HI rate `8.810144884444067e-13 s^-1`; nominal two-coefficient fit `7.926186875920432e-13 s^-1`. Its deterministic EOS+Jeans envelope is `[6.517910382457205e-13,9.912652064787459e-13] s^-1`; conditional scalar95 `[5.695493254096713e-13,1.134401796794173e-12]`; conditional joint2_95 `[5.50748186225509e-13,1.1731273824714687e-12]`. The seven-point table for all six moments, rate Jacobians and three envelope levels is in `results/RESULT.json`.

With supplied fixed target fractions, `P_X=y_X Gamma_X` and `Q_X=y_X heat_X`; supplied threshold I_X yields ionization energy `I_X P_X` and absorbed photon energy `I_X P_X+Q_X`, no double counting. In an evolved state the missing `D_a y_X` must be included. For mean scale factor clock `x=ln(a/a_ref)`, `dz_m/dx=-(1+z_m)`; rate derivative is `-(1+z_m) R_X [d ln R^P_X/dz_m+ln(10) kappa]`. At Puchwein knots, derivative is one-sided. Observed directional Bianchi redshift is not yet mapped.

BASS tau row `d tau/dx=K ne/H` gives only algebraic tangent `K/H D_a ne-K ne/H^2 D_a H`; actual ne/H derivatives and source-to-chemistry response are absent. No optical-depth physical error or native25 radius follows from the rate-only Jacobian.

## 검증·실패 보존

Actual Python3.13.5 NumPy/SciPy available, one new bounded source-rate run exit0, 21 grouped unittest methods PASS, actual `CPU_user=1.20s,CPU_sys=0.08s` for the final test run; no original campaign replay. Independent QR whitened GLS, q0 256 corner extrema at 3 redshifts, q2 ellipsoid support witness, rate Jacobian/Hessian finite differences, MP80 mean-clock derivative, positive Taylor remainder, photoenergy ownership, domain/zero/missing input controls. Initial binary64 clock FD failure `1.63e-9` relative was corrected with MP80 test reference without tolerance widening; two test-only `repr(np.float64)` conversion errors preserved. CAS first tau-check had operator-precedence error; corrected Wolfram run yielded five zeros and True. This is an independent *algorithmic* check, not a different-author R6/C9 review.

The repository-wide prior PR260 `verify` CI run `40787448721` failed at legacy Rust `cargo fmt --check`; its `cargo test` was SKIPPED. It does not negate this bounded Python result, but repository CI is not globally green.

## 판정 및 다음 물리 입력

R1–R5,R7–R10 and C1–C8,C10 are completed scoped: **18/20**. R6/C9 true independent-author review **NOT_RUN**. Original working DAG **33/88**, central last **28/88**, new original-node delta0; F4 PARTIAL, L4_ready=false, actual temperature/native25/physical radii null. No new IVP, no new active H–Li species, no new rate beyond Puchwein H/He table, no figure render, no main/owner merge. Historic exhausted caps and UNKNOWN_NOT_ZERO are not reset; new local analytic run is not charged as an authorized main campaign.

The next physical step requires actual named `D_a n_e`, `D_a H`, source-to-chemistry Jacobian and initial conditions, BASS K numerical identity, observed-directional-redshift map, and physical error/norm ownership. Until those are supplied, this is an **implementation-verified conditional UVB source port**, not a physical optical-depth or cosmological source-error certificate.
