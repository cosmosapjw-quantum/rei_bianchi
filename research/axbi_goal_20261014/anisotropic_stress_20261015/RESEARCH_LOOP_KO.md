# REI-AXBI: \(\Sigma=|\sigma|/H\), radiation/matter \(\pi_{ab}\)의 실제 이론·코딩 연구 루프

2026-10-15 KST · 사용자 의도: 기존 source-locked non-tilted LRS Bianchi-I H/He 재이온화 목표를 유지하면서, **발표와 관측량에 q_ref가 아니라 양의 Hubble-normalized 전단 \(\Sigma\)**를 쓰고, radiation 및 matter anisotropic stress \(\pi_{ab}\)를 실제 Einstein+에너지 방정식에 넣는다. 이전 [rei_bianchi PR129](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/129) head `fa20d75e344a28c833a47cbca82315ccbbdf6882`에서 새 isolated worktree/branch `research/rei-sigma-pi-coupled-20261015`로 작업한다. 원래 owner checkout, 실험 원본, H/He 비율, frozen `q_ref` input, 과학 Rust binary와 original signed checkpoints를 **변경하지 않음**. Native subagent tool 미노출 `NOT_RUN`; local Codex `NOT_USED`. 아래 신규 native Rust 연산은 `research/` opt-in 모듈이고 실제 오래된 HHe solver 재실행은 아니다.

## 1. 명확한 scalar \(\Sigma\) normalization과 기존 연구의 호환성

Metric signature \((-+++)\)이고 proper time \(t\)는 초(s). \(ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2\). 축방향 부호를 유지하는 내부 state \(s=\dot b\), ortho-normal shear는 \(\sigma^i{}_j=\operatorname{diag}(-s,-s,2s)\). 그러므로 \( \frac12\sigma_{ij}\sigma^{ij}=3s^2\), \(|\sigma|=\sqrt3|s|\), **사용자가 요청한 관측 변수**는
\[
\boxed{\Sigma=\frac{\sqrt{\sigma_{ij}\sigma^{ij}/2}}{H}
        =\frac{\sqrt3\,|s|}{H},\qquad
        \varepsilon_\sigma=\operatorname{sgn}s.}
\]
문헌의 Wainwright–Ellis normalization 중 \(\Sigma_{\rm WE}^2=\sigma_{ij}\sigma^{ij}/(6H^2)\)는 이 실험에서 \(\Sigma_{\rm WE}=\Sigma/\sqrt3=|s|/H\)임을 명시한다. 기존 original `BACKGROUND_FAMILY_LOCK.json`의 `Sigma_definition="s/H instantaneous"`는 부호가 있는 tetrad component에 해당하고, **새 user-defined scalar \(\Sigma\)와 같지 않다**. 그 파일의 hash를 바꾸어 과거 과학 입력의 재현성을 훼손하지 않고 새 adapter/metadata를 제공한다.

예전 초기 signed 입력값 \(q_{\rm old}=s_{\rm ref}/H_{\mathrm{FLRW}}(a_{\rm ref})\)은 이력 검증을 위한 private provenance로만 복원한다. 초기 복사장이 등방이고 stress/thermal correction이 아직 없는 동일 ref event에서
\[
\Sigma_{\rm ref}=\frac{\sqrt3 |q_{\rm old}|}{\sqrt{1+q_{\rm old}^2}},
\qquad q_{\rm old}=\varepsilon_\sigma\frac{\Sigma_{\rm ref}}{\sqrt{3-\Sigma_{\rm ref}^2}}.
\]
따라서 이 연구의 **public API, plots, stats, next physical variants는 \(\Sigma_{\rm ref}\)와 축방향 부호**를 사용한다. 사용자가 \(q_{\rm old}\)에 의존하도록 요구하지 않는다. \(\Sigma\) 하나로는 signed quadrupole, shear sign crossing을 정의할 수 없다.

원본 4개 완료 결과의 source SHA를 검증하고 새 converter `radiation_replay.py`로 \(\Sigma\) 및 \(\Pi_{\rm radiation},\Pi_{\rm ionizing}\)를 독립적으로 환산했다. 예: 대칭축 부호가 음이고 \(\Sigma_{\rm ref}=0.01731964211523148\)인 원래 case는 \(\bar z=4\)에서 \(\Sigma=0.001999901873216997\), \(\Pi_{\rm effective\,rad}=+1.39174972093\times10^{-13}\,\mathrm{J\,m^{-3}}\), \(\Pi_{\rm ionizing}=+1.50824894089\times10^{-20}\,\mathrm{J\,m^{-3}}\). Effective \(\rho_r\) free-streaming quadrupole를 새 14차 exact coefficient code로 real 312238 states에서 재구성한 최대 상대-iso density discrepancy \(2.286\times10^{-15}\). 이 original radiation stress는 당시 **prescribed background의 사후 보고량**이고 Einstein shear RHS에 되먹임되지 않았다.

## 2. \(\pi_{ab}\) 포함 Einstein 방정식의 정확한 유도와 보존식

압력 anisotropy는 ortho-normal frame에서
\[
\pi^i{}_j=\operatorname{diag}(-\Pi,-\Pi,2\Pi),\quad
\Pi_A=\frac{p_{\parallel,A}-p_{\perp,A}}3,\quad
\Delta P_A=p_{\parallel,A}-p_{\perp,A}=3\Pi_A .
\]
모두 압력/에너지밀도 단위 \(\mathrm{J\,m^{-3}}\). \(\sigma_{ab}\pi^{ab}=6s(\Pi_r+\Pi_m)\). \(K=8\pi G/c^2\) 사용(\(\rho\)는 SI 에너지밀도, \(s,H\)는 \(\mathrm{s^{-1}}\))하면
\[
\dot s+3Hs=K(\Pi_r+\Pi_m),\qquad
3H^2=K(\rho_{\rm dust}+\rho_{\rm th}+\rho_r+\rho_\Lambda)+3s^2 .
\]
Radiation / matter가 에너지를 서로 교환하지 않는 pilot에서
\[
\dot\rho_r+4H\rho_r=-6s\Pi_r,\qquad
\dot\rho_m+3H(\rho_m+p_m)=-6s\Pi_m .
\]
총 제약식을 proper time 미분하고 이 세 식을 사용하면
\[
\boxed{\dot H=-\frac K2\left[\rho_{\rm dust}
 +(\rho_{\rm th}+p_{\rm th})+\frac43\rho_r\right]-3s^2},
\]
즉 signed \(\pi_{ab}\) 항은 constraint derivative에서 **정확히 소거**된다. Spatial Einstein components \(G^\parallel{}_\parallel-G^\perp{}_\perp=3(\dot s+3Hs)\)도 확인. Local Wolfram Engine15 exact symbolic `verify_sigma_pi.wl`: tensor contraction, directional Einstein, Raychaudhuri energy, matter heat work, radiation integrated moment \(M'_0+2M_2=0\) (series to order 8) 모두 **PASS**, diagnostic stdout 보존. 문헌 검토: [Caceres et al. 2010](https://arxiv.org/abs/1003.3491) normalization/orthonormal shear caution, [Bittencourt et al. 2017](https://arxiv.org/abs/1610.00020) causal shear-viscous models. 이번 모델은 latter의 full Israel-Stewart 유도/claim을 채용했다고 선언하지 않는다.

## 3. 실제 구현한 radiation과 matter constitutive model

**Radiation:** \(f_{\rm fs}\in[0,1]\)는 original effective total \(\Omega_r\) 가운데 등방 initial collisionless-free-streaming으로 전파하는 분율이다. \(D(\mu,b)=(1-\mu^2)e^{-2b}+\mu^2e^{4b}\)에서
\[
M_0(b)=\tfrac12\int_{-1}^1D^{-2}\,d\mu,\quad
M_2(b)=\tfrac12\int_{-1}^1P_2(\mu)D^{-2}\,d\mu,
\]
\[
\rho_r(a,b)=\rho^{\rm iso}_r(a)[1+f_{\rm fs}(M_0-1)],
\quad
\Pi_r(a,b)=f_{\rm fs}\rho^{\rm iso}_r(a)M_2/3,
\quad M_0'(b)=-2M_2(b).
\]
\(f_{\rm fs}=1\)은 **모든 effective Ωr의 free-stream envelope**이며 원래 HHe ionizing radiation source와 다르다. 실제 CMB+neutrino+ionizing 세부 population별 physical \(f_{\rm fs}\)는 이 pilot에서 확정하지 않는다. \(f=0\)은 isotropic radiation 및 완전유체 stress-free reference. M0/M2는 기존 [PR125](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/125) source-locked Taylor14, crosschecked evolved-current-sky GL128.

**Matter:** 원래 cosmological dust rest-energy \(\rho_{\rm dust}\propto a^{-3}\)와 전단발열 internal reservoir \(u\)를 구분한다. \(\gamma_{\rm th}=5/3\), \(p_{\rm th}=(\gamma_{\rm th}-1)u\). 명시한 local constitutive **pilot**는
\[
\Pi_m=-2\eta s,\quad
\eta=\nu\rho_{\rm dust}/H,\quad
\nu\in[0,0.1],
\qquad
\dot u+3\gamma_{\rm th}Hu=-6s\Pi_m=12\eta s^2\ge0.
\]
이는 1차 instantaneous relativistic shear viscosity toy로서 인과적인 full Israel–Stewart matter model은 아니다. 특정 baryon/electron/collisionless CDM의 kinetic cross-sections나 thermodynamic viscosity가 실증되지 않았으므로 \(\nu=0.02\)는 단지 물리적 영향을 측정하는 exploratory knob. 실제 cold photoionized HHe temperature \(T_{\rm gas}\)와 새 matter internal \(u\)는 **동일량으로 대체하지 않는다**.

**RHS implementation:** `coupled_pi.py`에서 \(x=\ln(a/a_{\rm ref})\), dimensionless \(v=s/H_{\rm ref}\), thermal \(u/\rho_{\rm crit,0}\), \(\tau=H_{\rm ref}t\)를 DOP853/GL128 or Taylor14로 통합. Python `run_experiments.py`는 5 initial \(\Sigma_{\rm ref}\)/orientation state (0, ±0.008660146, ±0.017319642), \(f=0,\nu=0\) stress-free, \(f=1,\nu=0\) radiation \(\pi\), \(f=1,\nu=.02\) both-stress, 총 **15 실제 모델 해**를 계산했다. 모두 source-bounded \(a=1/21\to1/5\), no ionizing source or chemistry. Additive independent std-only Rust `sigma_pi_rhs.rs`는 동일 \(\Sigma\) API/energy/matter stress source로 108개의 실제 Python DOP853 sampled state-RHS comparison을 통과했다. Existing frozen AX08 binaries unchanged.

## 4. 실행으로 얻은 실제 stress-coupled 결과

공통 초기 \(\Sigma_{\rm ref}=0.01731964211523148\), \(\varepsilon_\sigma=+1\) 시 \(\bar z=4\):

| conditional scenario | final \(\Sigma\) | final signed \(b\) | final \(\Pi_r\) [J/m³] | final \(\Pi_m\) [J/m³] |
|---|---:|---:|---:|---:|
| stress-free | 0.00199990187348 | 0.00589291669527 | 0 | 0 |
| \(f_{\rm fs}=1,\nu=0\) | 0.00198260955166 | 0.00588351626100 | \(-1.37789\times10^{-13}\) | 0 |
| \(f_{\rm fs}=1,\nu=0.02\) | 0.00166995138632 | 0.00556295841189 | \(-1.30312\times10^{-13}\) | \(-1.16455\times10^{-12}\) |

Radiation feedback alone \(\Sigma\) suppression **0.86466%**, illustrative matter+rad suppression **16.4983%** relative to the common stress-free case. Matter Pi at that endpoint ~8.937 times effective rad Pi in magnitude for **chosen \(\nu=.02\)**. \(\gamma_{\rm th}=5/3\) thermal reservoir positive, viscosity shear dissipation positive; expected FLRW when \(\Sigma=0\) for all ν. Values for other initial Sigma and opposite orientations in `results/experiment.json`.

**New consequence beyond original AX08:** since
\[
M_2(b)=-\frac85b+\frac87b^2+\cdots,
\]
anisotropic radiation pressure is **not exactly odd** in b. Thus at a given initial \(|\Sigma_{\rm ref}|\), opposite \(\varepsilon_\sigma\) solutions have \(b_+(a)+b_-(a)\ne0\) after radiation feedback, unlike exact stress-free parity of original legacy histories. Measured final \(b_++b_-\) is \(1.24871872950\times10^{-8}\) at \(\Sigma_{\rm ref}=0.0086601458\) and \(4.99464385033\times10^{-8}\) at \(\Sigma_{\rm ref}=0.0173196421\). This is source-free radiation physics of the new self-coupled model, **not** a newly observed population inference.

Plots `results/coupled_sigma_pi_radiation_matter.png`, `results/radiation_stress_breaks_signed_b_parity.png`, `results/source_vs_coupled_Sigma_and_Pi.png`. Original source overlay is SHA-pinned, and re-evaluating original geometry at *exact original scales* gives maximum \(\Sigma\) difference \(8.674\times10^{-18}\) (after explicitly correcting an initial plot-grid interpolation artefact that was \(\sim10^{-8}\)). Do not interpret display-grid interpolation as physical solution error.

## 5. 물리·수치 검산 / 성능

- `test_coupled_pi.py`: **11/11 PASS**. Included tensor shear norm, \(\Sigma\) and sign adapter, Pi work, M0'/M2, local angular GL128, FLRW, true stress-free dust limit, pressure sign, viscous heat nonnegative, q→−q parity breaking, time refinement, evolving GL128 vs Taylor14.
- `rust/rei_microphysics/tests/axbi_sigma_pi_rhs.rs`: **4/4 PASS**, including **108 actual Python-evolved state RHS** cross-language, native tensor invariants, physical zero/default cases, domain adversarial tests. Rust module `sigma_pi_rhs.rs` uses exact previously tested radiation coefficients, and does not overwrite production `axbi_driver.rs`.
- `radiation_replay.py`: verified 4 actual original cases' exact SHA history+feedback, 312238 rows each and original effective radiation pressure anisotropy vs 14th-order analytic moments, max iso-normalized difference ~\(2.29\times10^{-15}\). Saved source ionizing \(\Pi\) still stored **separately** from effective CMB/free-stream radiation \(\Pi\) and must be recoupled with actual source/sink energy ledger before true coupled astrophysics.
- `verify_sigma_pi.wl`: **Wolfram exact symbolic PASS**, all tensor, Einstein, energy, 8th-order radiation moment identities. Python constraint/energy/Raychaudhuri residuals of the actual 15 simulation runs peak \(\sim1.4\times10^{-15}\).
- Matched error microphysics ODE benchmark `bench_solver.py`: GL128 versus Taylor14 solve 4 independent physical scenarios, **same evolved state error** max ~\(4\times10^{-15}\) in normalized clock, 7 measured repeats. Median 4-case wall: Taylor14 **0.04118s**, GL128 **0.04792s**, only **1.164×** speedup for this *whole toy coupled-background integration*. 2-thread Taylor14 **0.04387s**, slower (\(0.939\times\) serial speedup), so single-thread vector/test default selected. Do not extrapolate previous PR125 2000× isolated moment micro-kernel speedup to full H/He ODE.

## 6. 변경된 DAG

Machine-readable `NEXT_DAG.json`:
- Verified new Sigma adapter (AX_SIG_01), self-consistent collisionless radiation stress Einstein/energy (AX_PI_RAD_02), matter viscosity+heat pilot (AX_PI_MAT_03), cross-validated Rust (AX_PI_RUST_04), four **original** source Pi readout (AX_PI_ACTUAL_05).
- Still-open physical matter \(\pi_{ab}\) closure (AX_PI_MAT_06): select baryon/electron, collisionless dark matter kinetic distribution or tilted/multifluid source, and derive \(\pi_{ab}\) from its transport. True causal Israel-Stewart relaxation must add complete non-equilibrium energy/entropy and appropriate closure.
- True H/He radiation/atomic source+stress coupled REI solver (AX_PI_COUPLED_HHE_07): integrate \(\Pi_{\rm ionizing},\Pi_{\rm CMB},\Pi_{\rm matter}\) with original species/thermal photon/matter energy ledgers. Source identity will be **new**; do not resume old AX08 checkpoints from a source changed by new physics. Reuse [AX03 PR127](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/127) actual chemistry-clock correction and [SOURCE07 PR128](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/128) dynamic photon/absorption pilot conditionally after matching respective physical assumptions.
- Full new \(\Sigma\)-based temperature, ionization, stress, observational source/clock convergence AX11 and AX12 remain pending, and observer optical depth tail is unmeasured. Historical previous [BASS_HE PR64](https://github.com/cosmosapjw-quantum/BASS_HE/pull/64) 16-cell warm P01 tau is another source, not secretly inserted into this cold run.

**Scientific admission:** `SOURCE_FREE_RADIATION_AND_PHENOMENOLOGICAL_MATTER_PI_COUPLED_BACKGROUND_NUMERICALLY_VERIFIED`; physical stress-coupled primordial H/He reionization and observer predictions `NOT_ISSUED`. Full original 5-case AX08 PLUS recovery and native H/He source-bound AX11 remain separate tasks; no full observational/novel result is asserted.


## 7. 완결된 \(\Sigma,\pi_{ab}\) numerical histories 및 source comparison

새 `export_sigma_pi_history.py`는 15개 실제 source-free+viscous coupled-background ODE의 501점 진화결과 **7,515행**을 `results/coupled_full_Sigma_Pi_history.csv` (2.2MB)에 공용 과학 변수로 기록한다. 열에는 \(\Sigma_{\rm ref}\), \(\varepsilon_\sigma\), \(f_{\rm fs}\), \(\nu\), \(a\), \(\bar z\), proper elapsed \(t\), signed \(b,s\), \(\Sigma,\Sigma_{\rm WE}\), \(\Pi_{\rm rad},\Pi_{\rm matter},\Pi_{\rm total}\), dust/thermal/radiation \(\rho\), thermal \(p\), Hamiltonian shear fraction이 있다. q_ref를 Primary output API나 figure legend에 사용하지 않는다. 모든 행에서 \(\Pi_{\rm total}=\Pi_{\rm rad}+\Pi_{\rm matter}\)와 \(\Sigma=\sqrt3\Sigma_{\rm WE}\)를 확인했다.

원본 minus 완주 history의 실제 \(a_i\) 각각에서 **보간 없이** \(s(a)=s_{\rm ref}(a_{\rm ref}/a)^3\), \(H(a)=\sqrt{H_{\rm FLRW}^2+s^2}\)를 직접 계산하면 저장된 원본 \(\Sigma\)와의 최대 차이는 \(8.673617379884035\times10^{-18}\). 별도 신규 stress-free ODE도 endpoint와 정확히 일치한다. 이 검사는 이전의 1101-point plot interpolation이 1.37e-8 수준의 *표시 보간 오차*를 불필요하게 만들던 초기 오해를 교정한 것이다. 실제 물리 error로 표시하지 않는다.

최종 재검증: Python 신규 물리 테스트 **11/11**, std-only native Rust 신규 **4/4** (108 physical sampled RHS states) 및 기존 AX03 background regression **6/6**, 합계 **21/21 PASS**. Local Wolfram exact GR + energy identity **PASS**. 개별 출력값과 실제 이력의 provenance, benchmark and raw-size manifest를 `RESULT_STATUS.json`과 `SOURCE_MANIFEST.json`에 잠근다. `NEXT_DAG.json`은 잠재적으로 더 현실적인 viscous matter / kinetic closure·true HHe radiation source/opacity feedback·AX11 등 별도 미수행 stage를 machine-readable 형태로 남긴다.
