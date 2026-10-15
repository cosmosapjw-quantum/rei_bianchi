# HE18 → rei_bianchi: signed-q cold Thomson optical-depth analysis (2026-10-15 KST)

**Evidence classes:** DERIVED (normal congruence, shear invariants, time-slice decomposition); NUMERICALLY_CHECKED (source-scoped full and prefix histories); IMPLEMENTATION_VERIFIED (Ubuntu tests and postprocessing); UNRESOLVED (native ODE global error, certified physical attribution).

## 핵심 결과 요약 (한국어)

이 루프는 warm BASS_HE HE18 16셀 자료를 cold 모델 결과로 혼용하지 않으면서, 같은 원본 소스에서 계산된 다섯 개의 signed-shear prefix를 이용해 Thomson 광학깊이의 짝/홀 응답을 직접 계산했다. 공통 평균 스케일 인자 a=0.08873654701704167에서 E(0.01)/E(0.005)=3.99986519이며, E(0.005)=-2.76081465e-8이다. 공통 proper-time 분해에서 E의 약 90.4155%는 종점 clock 차이에 해당하고, 약 9.5845%는 같은 proper-time까지 적분한 전자밀도 이력 차이에 해당한다. 이 비율은 선정한 clock decomposition과 입력 이력에 조건부이다.

이미 AX08가 산출한 J2 photon angular moment의 odd scaling은 최신 로컬 결과·소스 SHA와 직접 교차검증하여 재사용했다. 별도 기여로 중복 계산하지 않는다. 원 파일 SHA와 source epoch를 묶은 NPZ 캐시는 반복적인 교차진단을 가속한다. native coupled ODE의 진정한 전역 오차상계, 관측 CMB 전체 tau 및 편광 예측은 아직 보증하지 않는다. 원래 solver와 산출물은 변경하지 않았다.

## Input identity, frozen scope

- Original cold AXBI owner: rei_bianchi, branch codex/rux-science-delivery-20261014 at HEAD 0fcb2dddf5de6b583c2e00f150abff0b2afb6315, left unchanged.
- Prior isolated HE18 adapter branch: research/bass-he-optical-depth-transfer-20261015, parent e3921c3320f2bccd82661859365826ac4c72ae18.
- Five signed-prefix CSVs from research/axbi_goal_20261014/runs/{paired,flrw}/32d11e733155/{case}/history.csv, 200001 rows each, a_end=0.08873654701704167 (zbar=10.269313869154184). All source_identity.txt digest exactly d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185. All have status STOPPED_CHECKPOINTED and scientific_admission=NOT_ISSUED, not "full histories".
- The separate warm BASS_HE HE18 16-cell campaign has archive SHA 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d. Its FT03/HM12 microphysics, helium ratio 3/38, temperature, and tau numerical values are not transferred to cold Plancklike_MD14_BB50K. Only the calculation and error-control design is relevant.
- For cold histories f_He=1227/15092, proper n_H and n_e in cm^-3, t in proper s elapsed from mean zbar20. Diagnostic tau uses sigma_T=6.6524587321e-29 m^2 and c=299792458 m/s, with ne[cm^-3] -> 1e6 ne[m^-3].

## Theoretical construction and CAS check

Use (-,+,+,+) and non-tilted homogeneous normal-comoving electrons. The original AX08 convention is ds^2=-c^2dt^2+a^2exp(-2b)(dx^2+dy^2)+a^2exp(4b)dz^2. An earlier alternate notation beta=-b describes the same metric, but MUST NOT be silently identified with b. Optical depth from emission t_e to observer t_o is tau=integral sigma_T c n_e(t) dt, a scalar independent of photon direction if the same proper endpoints are used. Redshift at fixed direction is anisotropic, and t_e at fixed observed directional redshift is not generally common.

For a uniform *reference covector* direction mu=p_z/|p|, the photon energy factor is F(mu,b)=sqrt((1-mu^2)exp(2b)+mu^2 exp(-4b)). Wolfram expansion gives <F>=1+(8/5)b^2-(16/21)b^3+(8/35)b^4+O(b^5): linear vanishes but cubic need not. This angular averaging measure differs from the native source's current-local-ray mu, which enters the moment J2=sum_{k,i} N_ki E_i P2(mu_k). Neither expression is a source-independent prediction for the other. LRS tracefree shear diag(s,s,-2s) has trace 0, trace(sigma^2)=6s^2, trace(sigma^3)=-6s^3. Hence no universal parity-even theorem under q->-q; analytic isotropic scalar functionals of the shear alone lack a linear invariant but can contain cubic invariants. Additional anisotropic data or tilt can even introduce linear terms.

Definition of case-comparison diagnostics at same mean scale factor a: E(q,a)=[tau(+q,a)+tau(-q,a)]/2-tau(0,a), O(q,a)=[tau(+q,a)-tau(-q,a)]/2. For a shared proper time t*(a)=min_q t_q(a), define E_t(q,a) at that same t* and E_clock=E(q,a)-E_t(q,a). The identity is algebraic and reference-dependent; E_t is NOT a purely atomic-microphysics contribution.

## Five real stored histories: results

At shared endpoint mean a=0.08873654701704167 (zbar=10.269313869154184):

| Quantity | Value |
| --- | ---: |
| tau(0) | 0.00307215160948680604 |
| E(0.005) | -2.76081465256e-8 |
| E(0.01) | -1.10428864310e-7 |
| E(0.01)/E(0.005) | 3.99986519225 |
| O(0.005) | ~1.52e-18 |
| O(0.01) | ~-1.08e-18 |
| E_t(0.005) at earliest common proper t | -2.64609998416e-9 |
| E_clock(0.005) | -2.49620465414e-8 |
| E_clock / E at 0.005 | 0.90415510213 |
| E_t(0.01) | -1.05840587801e-8 |
| E_clock(0.01) | -9.98448055303e-8 |
| E_clock / E at 0.01 | 0.90415496124 |

At a = 0.055, 0.060, 0.070, 0.080, 0.088736547, the clock fraction for q=0.005 is respectively about 0.9314, 0.9070, 0.8859, 0.8890, 0.9042. This is an **operational split**. In particular, the fixed-proper-time residual remains gravitationally coupled and is not an autonomous atomic reaction-rate effect.

Same |q| sign-paired prefix source rows show exactly identical stored t and a in all 200001 rows. For q=±0.01, max absolute difference in ne is 3.2526065e-19 cm^-3, x_HII 4.718448e-16, x_HeII 1.915135e-15. For q=±0.005, corresponding ne difference is 1.664420e-19 cm^-3. The odd tau differences are near summation and stored-data precision, not a detected physical cubic coefficient. ZERO and four signed prefixes share the identical cold source epoch hash above.

The maximum difference in **one input history** between full-resolution and every-8th-row trapezoid integration is ~7.42e-13 in tau at this endpoint. Decimation is NOT an interval error certificate and is not comparable to an accepted source-ODE global tolerance. The native run's final "last_error" diagnostic (~2.64e-6) cannot be converted directly to a tau uncertainty without an appropriate goal-oriented sensitivity argument.

## Full zbar 20 → 4 histories

Read-only full composed histories for ZERO, SHEAR_MINUS(q=-0.01), SHEAR_HALF_PLUS(q=+0.005) each contain 312238 rows and have valid recorded full-history SHA fingerprints. Their cumulative tau are respectively 0.03196818283862119, 0.03196792354404614, 0.03196811801369409. Only these three are in the fully composed set verified here. No even/odd full-zbar4 estimate is admitted because the complementary +0.01 and -0.005 composed histories were not verified complete.

## Implementation and optimization

- Signed source-only reader and explicit five-case stencil; normal electron census reconstruction; cached tau and normal-time interpolation at shared mean a and shared proper t.
- Signed source input hashes, executable source epoch, and compressed cache hashes preserved, verified on read. Cache is analysis-grade, not new scientific authority.
- On Ubuntu: raw SHA+CSV five prefix reads approximately 7.185 s summed; provenance-cache reload 0.155 s (~46x shorter for repeated analysis, not matched full solver throughput). Five raw source prefix files are roughly 576 MiB combined, caches approximately 26 MiB (du rounded), a substantial space reduction; exact sizes depend on the filesystem.
- Earlier postprocessing real two-case sequential 4.711 s / two-process 2.381 s (~1.98x); this did not optimize the native Rust solver.
- Compensated/extended accumulation diagnostics and factor-exact finite-decimal conditional bounds are separate; a true source ODE interval enclosure remains unavailable. Data-processing subworkers are distinct from native model subagents, which were NOT_RUN.
- White-background research figure: signed_q_20261015/SIGNED_TAU_CLOCK.svg.

## Verification and next meaningful science gate

Local Ubuntu Python regression suite: 27/27 PASS before final publication (see new tests). Wolfram algebra: angular energy expansion and shear invariants evaluated; no local xAct call in this run. Sources (literature basis): Friedrich et al. 2012 MNRAS 421, 2232 (H/He coupled C2-Ray), https://academic.oup.com/mnras/article/421/3/2232/1077406. Publication-grade q^2 claim remains on hold until at least a second independently converged native ODE grid/tolerance, solver discrepancy bound for tau and photon collision history, and source-consistent physical attribution are available.

**Positive next action:** run paired q=0, ±0.005, ±0.01 with tighter time-step/error settings or independent method over the *same* mean-a prefix (not a full 5x campaign by default); propagate error into E_t and E_clock; measure cubic angular odd effects in observables carrying direction (J2/CMB morphology), not just the angle-averaged scalar tau.


## Pre-existing AX08 angular-moment source readback

The original AX08 thread already had the signed-prefix J2 result (2026-10-15). Its exact file research/axbi_goal_20261014/convergence/ax08_half_plus_20261015/signed_prefix_parity.json was matched to all five original history SHA256 identities. In rust/rei_microphysics/src/axbi_driver.rs, J2 is exactly the energy per H angular quadrupole sum of photon stock times energy times P2(mu_current). Native source snapshot SHA256 in this run: 92bc6ca1540c927cde7452d218f666882ecdd651558b151b31e9a6a8e2d92c8f. The independently preserved J2 odd endpoint is -2.667171197077781e-12 eV/H at q=0.01 and -1.3335886533020386e-12 eV/H at q=0.005, ratio ~1.99999542. The new optical-depth even ratio is ~3.99986519. It is incorrect to label this saved photon spectral angular moment as a temperature quadrupole or CMB polarization without the subsequent Thomson transfer calculation.

## Repeatable five-source parallel I/O comparison (measured)

- Five-history exact JSON numerical identity check: PASS. Sequential subprocess wall 8.073401 s; 2-worker wall 4.883689 s; speedup 1.653136x.
- Raw source CSV bytes 601988551; provenance-cached NPZ bytes 26389839; on-disk reduction 22.8114x. Source files are not deleted or mutated.
- Native production solver was not profiled here; throughput numbers are only postprocessing.
