# REI SOURCE_AGE_AND_BIANCHI_REFINEMENT: source-age/angle/event oracle

2026-10-16 KST. **조건부 이론+샌드박스 코드 검산만**. 실제 Grackle/MD14 동적 native solver, NCP, 전체 EoR 계산은 이번 연구에서 NOT_RUN. 원래 owner PR160/PR150는 읽기만 했다.

## 기원 및 구별되는 범위

- Original finished REI PR160 HEAD: `8351f21036eeaa079e603159a08269dbe90ce58e`. 온도 의존 native RR/CI/DR·thermal owner 및 atomic rollback, 51 native focused tests, 203 mechanical checks, 4980 matched comparisons는 이전 증거이며 다시 구현하지 않는다.
- 조사된 REI PR150 HEAD: `6ea2b1b4b3875c9163cafc45efe720afded43fc4`, source005 z20→4와 source008 BASS component는 별도 production DAG, 본 작업은 변경하지 않는다.
- REI PR162: frozen-cell positive birth cancellation. BASS_HE PR71: frozen-opacity continuous-source phi1. bass_cr PR75: common-q/source-age bridge; BASS PR166: distinct geometry donor; REC PR99: separate recombination prehistory; WU088_HH PR96: physical rate HOLD.

**새 연산자:** 연속 photon birth-time `y`, `mu_birth`, physical birth energy `E_b`에 따라 signed LRS Bianchi Killing energy/physical-work를 계산하고, 원래 Verner (1996) HI/HeI/HeII fits에 대한 다중 threshold event-splitting 및 positive exponential competing absorption을 수행한다. Age global GL/age terminal-cut panels/embedded GL4-8 adaptive와 angular global GL/terminal cut panels를 비교하며 independent DOP853 ODE로 검증한다. Full native chemistry/source provenance 결합은 아직 하지 않았다.

## 물리 convention, source/fit/ledger

`ds²=-c²dt²+a²[e^(-2b)(dx²+dy²)+e^(4b)dz²]`, `s=db/dt`, `v=s/H`, `Sigma=sqrt(3)|s|/H`, `x=ln(a/a_ref)`, `a_ref=1`, `y=x_birth`.

`R²=(1-mu_b²)e^{2[b(x)-b(y)]}+mu_b²e^{-4[b(x)-b(y)]}`, `E=E_b e^(y-x) R`, `mu²=mu_b² e^(-4db)/R²` and `-dE/dx=E[1+v(x)(3mu²-1)]`. Nonnegative emitted source `j(y)` has units photons per initial H per **dln a**; physical proper-time source is `H(y)*j(y)`. Real native PR150 reference-q normalization must be checked rather than guessed; birth q=a(y)E_b is source-age dependent.

Original Verner donor table 185-row provenance SHA256 `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`; only the three directly checked species rows are embedded in code. Fit activation chi_fit(eV) = (13.60,24.59,54.42); **physical native binding energy** B_i(eV)=(13.598434599702,24.587389011,54.41776), taken from original `HHeModel::controlled_fixture`. Keeping those distinct repaired a real energy ledger failure. For prescribed neutral `n_i ∝ a^-3`, H/Href=1, `k_i(x)=kappa_i e^-3x sigma_i[E(x)]/sigma_i(chi_fit,i)`, dimensionless hazard per dln a. Dynamic neutral abundance and temperature are **not** solved.

Source-free sharp age-integrated P_parallel-P_perp envelope (for arbitrary positive reflection-even sky at each independent birth epoch):

`-E_b/2 ∫dy j(y)e^(y-X+db) ≤ Π(X) ≤ E_b∫dy j(y)e^(y-X-2db)`, db=b(X)-b(y). Both extremes attained by transverse mu=0 and equal axial ±1 births. Algebra: with A=exp(2db), B=exp(-4db), z=mu_birth², transported pressure kernel `k(z)=[3Bz/sqrt(A+(B-A)z)-sqrt(A+(B-A)z)]/2` has derivative `[A(A+5B)+(B-A)(A+2B)z]/[4(A+(B-A)z)^(3/2)]>0`, since the affine numerator at z=0 and 1 is `A(A+5B)>0`, `2B(2A+B)>0`. Wolfram checked `{0,A(A+5B),2B(2A+B),0,0}`. **This sharp envelope does not carry over unchanged through angle-dependent absorption.**

Absorption ray solution `dN/dx=-N sum_i k_i`, `dA_i/dx=N k_i`, `dQ_heat/dx=N sum_i k_i(E-B_i)`, `dW/dx=-N dE/dx`. Number and energy budgets: `N_birth=N_survive+sum A_i` and `N_birth E_b=N_survive E(X)+sum B_i A_i+Q_heat+W_geom`. W can be signed when strong anisotropic expansion makes instantaneous blueshift. The code uses midpoint hazard with exact positive competing exponential per event panel; independent SciPy DOP853 solves the continuous six-variable RHS. The resulting conservation identity is not by itself convergence evidence.

## Actual numerical evidence, scope and failed controls

- Sandbox **34/34 Python pytest PASS**; independent DOP853, simultaneous  signed shear branches, original Verner fits and proper support events, source/energy ledger, zero shear isotropy, even μ reflection, spectral and adaptive test controls.
- First failed post-physics-improvement test: adaptive age aggregation used Verner chi_fit instead of native binding B_i, leaving energy residual `6.430365057e-5 eV/H`. Fixed by explicitly selecting native B_i, no widened tolerance. Saved raw `evidence/pytest_34_first_failure.log` and repaired result `evidence/pytest_final.log`.
- Event-aligned per-ray 8..256-step tests against independent DOP853 have tail log2 order ≈(1.9980,1.9839,1.9839) for v=(-.04,0,+.04). **Local frozen-opacity/geometry claim only**.
- Absorption-free sharp pressure bounds [eV/H], v=-.04: [-19.8040,41.2471]; v=0: [-20.0722,40.1444]; v=+.04: [-20.3453,39.0814], endpoints attained.
- Adaptive GL4/8 source birth integration at n_time=128: 336 birth/angle ray calls, independent DOP853/age-cut reference 520 calls; HeII absorption rel difference `1.3003e-7`, photoheat rel difference `4.8954e-6`; number residual ~1e-16 per H, energy ~3.20e-14 eV/H. Adaptive error estimator is empirical, **not** rigorous global enclosure.
- Signed v=-.04, age 24/time64, angular target16: global GL HeII absorption absolute error vs cut-GL64 ≈1.9097e-7 photons/H, terminal-cut GL ≈1.1125e-11. At target4, Pi absolute error **worsens** global 1.47e-4 → panel 2.87e-3 eV/H. No uniform angular superiority claim.
- Manufactured `b=.22 sin(18x)` (max |v|=3.96, **not near-FLRW**) has five re-entrant physical HeII cutoff roots for axial source at x≈(0.0526543,0.137418,0.355911,0.540303,0.663950). Refined result vs DOP853 remains provisional; the numerical event scanner must be checked for tangential (non-sign-changing) events before production.
- Manufactured positive blackbody energy nodes 8/16/32 show nonmonotone species responses, so **spectral convergence NOT_ISSUED**. No real MD14 SED, changing chemistry, Case-A escape spectrum, recoil or self-consistent Einstein dynamics has been inferred.

Reproduce with `bash verify.sh`; raw `evidence/SOURCE_AGE_NUMERICS.json`, two actual plots under `figures/`. Python3.13, numpy/scipy/pytest/matplotlib. No Rust/NCP/GitHub CI run in this sandbox cycle.

## Next READY

`SOURCE_AGE_NATIVE_OWNER_BIND`: exact Git source/ABI/restart adaptation to original PR160/PR150 `chemical_stage`, `PreparedAbsorption`, MD14 source-age cohorts; same-clock gas/source/geometry, once-only photo sink, proper-time vs x clock and q map, positive accepted trial/rollback; native reference parity and independent age/angular/energy/time refinement on NCP without restarting original full005. Include BASS PR166 signed geometry with physics and provenance firewall. Production scientific admission `NOT_ISSUED`. HH physical rate remains HOLD.

Original literature: Mellema et al., C2-Ray https://arxiv.org/abs/astro-ph/0508416 ; Friedrich et al. H/He extension https://arxiv.org/abs/1201.0602 ; Pawlik & Schaye multifrequency TRAPHIC https://arxiv.org/abs/1008.1071 ; Verner et al. original fit DOI https://doi.org/10.1086/177435 . These support method context, not uniqueness/novelty of this construction.