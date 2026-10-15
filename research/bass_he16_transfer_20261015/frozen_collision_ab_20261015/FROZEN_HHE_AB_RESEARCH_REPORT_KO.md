# HE18 → rei_bianchi: frozen H/He 충돌 A/B와 HeII 문턱 ghost-ionization (2026-10-15 KST)

## Evidence status and original physics boundary

**DERIVED / NUMERICALLY_CHECKED / IMPLEMENTATION_VERIFIED** for a bounded, *frozen-gas* photon experiment with original Rust library functions; production AXBI ionization-history global error and observable validity remain **HOLD**. User's local Codex was not used. The original rei_bianchi solver branch, original nine native runs and earlier warm HE18 16-cell reference archive were read-only.

The original stored cold AXBI solver binary (SHA256 `32d11e733155d355a1fa748597b48ea1c8196adba3c871722a7a598f0b6cbfca`) and its compiled source (SHA256 `d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185`) are **different whole-source/binary epochs** from the separately linked `librei_microphysics-2db3552c92b16edc.rlib` (binary SHA `44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f`, full compiled source SHA `fa00a6f73f45e8ac391b5bb723b30d162005bf79750138b1a13e84ec82248f67`). Twelve tested transport/background/atomic function bodies including `Driver::geometry_map`, `Driver::deposit`, `AtomicProvider::cross_section` and `HHeModel::controlled_fixture` match byte-for-byte across those original source records. The optional `axbi_q_reference::absorb_frozen_gas` belongs to the separately linked reference library and has not been represented as a frozen production BE chemistry operator.

**No warm FT03/HM12 physical state, reaction rates, temperature, photon stock or HE18 warm tau was substituted into cold AXBI.** The downstream cold program uses its own reference Verner HI/HeI/HeII cross sections, source energy registry and background. Literature context: [Friedrich et al. 2012](https://academic.oup.com/mnras/article/421/3/2232/1077406), [Norman et al. 2015](https://doi.org/10.1088/0067-0049/216/1/16), [Fleury, Pitrou & Uzan 2015](https://doi.org/10.1103/PhysRevD.91.043511).

## Experiment contract

**A: PROJECTED**. Use original `Driver::geometry_map` twice for each midpoint-split source step, meaning fixed physical-energy two-neighbor projection after each geometric half-step. For all occupied energy nodes, evaluate the **canonical grid-node energy \(E_i\)** with the original `AtomicProvider::cross_section` (matching original production `evaluate` spectral convention). Cache immutable H/He cross sections once and apply frozen exponential absorption at the same midpoint with exact `expm1` species competition.

**B: COVARIANT**. Use `CovariantPhoton::from_local` and `energy_at` preserving the three Killing-direction momentum components through expansion without intermediate grid projection. Apply the same frozen-gas exponential species absorption via the existing reference `absorb_frozen_gas` at each midpoint and exactly the same proper time interval.

The model geometry is LRS Bianchi I \((-+++)\), \(ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2\), \(z_{\rm bar}=20\to19.8\), \(q_{\rm ref}=-0.005,0,+0.005\). \(n_H(a)\) and \(n_{\rm He}(a)\) are taken from the native normal-comoving background. A controlled frozen neutral composition uses \(\eta\in\{0,10^{-6},10^{-5}\}\):
\[
n_{\rm HI}=\eta n_H,\quad n_{\rm HeI}=n_{\rm HeII}={\eta\over2}n_{\rm He},\quad x_{\rm HeIII}=1-\eta.
\]
The photon trace amount is \(N_{\gamma,0}=10^{-10}\) per hydrogen nucleus, far below the available absorbers for \(\eta>0\). These high-ionization \(z\simeq20\) states are deliberate **hypothetical controls**, not predictions for the actual reionization history or a dynamically solved thermal gas.

Original spectral energy indices \(5,20,32,33\) were examined with \(N_{\rm step}=1,32,256\), three signed \(q\) and three frozen absorber \(\eta\), generating **108 paired physical cases, 216 individual transport-lane records**.

## Native photon/atomic event ledger and analytical closure

The original reference coefficients are \(\lambda_j(E)=c\,n_j\,\sigma_j(E)\) for \(j=\mathrm{HI,HeI,HeII}\), \(\lambda=\sum_j\lambda_j\). For frozen \(\lambda\) over each source substep,
\[
N_{\rm abs}=N_{\rm before}[-\operatorname{expm1}(-\lambda\Delta t)],\qquad
N_{{\rm abs},j}=N_{\rm abs}{\lambda_j\over\lambda}.
\]
The ledger is
\[
B=\sum_jN_{{\rm abs},j}\chi_j,\quad
Q=\sum_jN_{{\rm abs},j}(E-\chi_j),\quad
B+Q=E N_{\rm abs}.
\]
Wolfram independently returned exactly zero symbolic residual for number and energy partition. \(\chi_j\) is the original source `HHeModel::controlled_fixture` binding threshold, not a new rate fit.

In each of the 216 runs the code checked:
- \(N_{\rm initial}=N_{\rm surviving}+N_{\rm absorbed}+N_{\rm grid-boundary}\) for A and the zero-boundary version for B.
- \(E_{\rm initial}=E_{\rm surviving}+B+Q+E_{\rm redshift-work}+E_{\rm grid-boundary}\) with original `geometry_map` photon_work/boundary ledger for A and exact characteristic redshift work for B.
- Three-species absorption partition and nonnegative gas photoheating, physical reservoir capacity and the original atomic binding threshold.

Measured maximum absolute **normalized** residuals across 216 records are \(1.94\times10^{-15}\) (photon number), \(1.98\times10^{-15}\) (energy) and \(1.25\times10^{-15}\) (species-event partition).

## Critical discovery: false HeII absorptions from projection onto a discontinuous threshold

The original energy registry has an exact \(\mathbf{54.42\ eV}\) node, and the original Verner `AtomicProvider` has a strict HeII photoionization condition \(\sigma_{\rm HeII}(E)=0\) when \(E<54.42\) eV. The published numerical constants give
\[
\sigma_{\rm HeII}(54.42~{\rm eV})=1.58728025754\times10^{-18}{\rm~cm^2}.
\]

Take a photon at the HeII threshold node. Along any of the tested expanding null trajectories its true characteristic energy falls below 54.42 eV for every \(t>t_{\rm emission}\). Therefore the exact covariant source physically gives **zero HeII photoionization** in this controlled experiment. However when \(\text{E}_{\rm lower}<E_{\rm exact}(t)<E_{\rm threshold}\), canonical positive two-neighbor interpolation puts
\[
w_{\rm threshold}={E_{\rm exact}-E_{\rm lower}\over
E_{\rm threshold}-E_{\rm lower}}>0
\]
on the 54.42-eV node, where the original source cross section is nonzero. The projected A trajectory therefore yields positive, purely numerical HeII events. This sign argument requires \(n_{\rm HeII}>0\) and controlled interval length; it is **not** a quantitative theorem for all grids.

Actual 256-step results at \(\eta=10^{-5}\), *per injected source photon*:

| \(q\) | \(N_{\rm HeII,PROJECTED}/N_{\gamma,0}\) | \(N_{\rm HeII,COVARIANT}/N_{\gamma,0}\) |
|---|---:|---:|
| -0.005 | 0.00246367659881134 | 0 |
| 0 | **0.00246475583249896** | **0** |
| +0.005 | 0.00246577523588119 | 0 |

At \(q=0\), \(\eta=10^{-5}\), 256 steps, the total original **binding-energy ledger** is \(0.277566641328993\) eV per injected photon in PROJECTED and \(0.143466406870282\) eV in COVARIANT, a difference of \(0.134100234458711\) eV per photon. Photoheating differs separately: \(0.299579659468956\) versus \(0.299883127280840\) eV per photon. Both independently close their energy and photon ledgers. The absolute false HeII event count is \(2.46475583250\times10^{-13}\) per hydrogen nucleus due to the deliberately small photon population \(N_{\gamma,0}\).

**Positive source control:** starting above threshold at native energy index 33 produces physically positive HeII events in both A and B. Starting well below threshold at indices 5 and 20 produces none in either arm. With \(\eta=0\) there are no absorption events in either arm; pure projected freeflight can nevertheless lose photons below the numerical support (e.g. index 5, 256 steps), whereas the covariant arm has zero artificial boundary loss.

## Separate floating-point threshold-owner issue and repair

The first source A/B used `CovariantPhoton::from_local` to reconstruct each *stored* grid-node energy when calling the absorber. For signed \(q\) an exact same-frame conversion can return \(54.4199999999999946\) eV rather than the canonical 54.4200000000000017 eV, a difference of one double-precision ulp \(7.1054273576\times10^{-15}\) eV. At the discontinuous HeII threshold that switches \(\sigma_{\rm HeII}\) from \(1.58728\times10^{-18}\) cm² to zero, producing a false negative in the projected arm for some coarse-step signed cases.

We preserved the initial frame-roundtrip source and raw reference results in separate files. The final A implementation instead uses the original **known energy-node \(E_i\)** directly, exactly as original production `Driver::evaluate` does. B always uses the characteristic photon energy. Positive phantom HeII events now occur in A at all three tested steps for every signed q, while B has exactly zero. This separates *projection-induced false photoionization* from *ULP-threshold misclassification*. No global source implementation was silently changed.

## Vectorization/parallel/compute optimization

An immutable `OnceLock` caches the three `Driver`/initial-state pairs rather than rebuilding 4096-panel backgrounds for 108 cases. A second immutable grid signature cache computes original Verner cross sections at 49 native fixed energy nodes **once** and reuses them across midpoint source events. Explicit two-worker bounded Rust case execution was implemented.

One actual user-Ubuntu execution of 108 source cases, 216 rows; same native A/B physics and **exact numerical-string identity across reference, cached serial and cached parallel** (excluding runtime diagnostics):

| Runnable | Wall time |
|---|---:|
| Canonical grid energy, no signature cache, serial | 45.30 s |
| Canonical grid energy, signature cache, serial | 44.56 s |
| Canonical grid energy, signature cache, two workers | 41.64 s |

Observed throughput advantage of both hoists+two workers versus the uncached serial is about **1.088×**, modest and hardware/load dependent; it is *not* an optimization of the full Rust reionization solver. SIMD/GPU production algorithms were not added or benchmarked. The original frame-roundtrip lane is a **different numerical physics contract**, so its runtime must not be treated as an apples-to-apples canonical acceleration benchmark.

## Reproducibility and scientific gate

- Rust original `librei_microphysics` rlib and separate frozen original AXBI binary are pinned distinctly by SHA256; tested atomic/transport source surfaces match for 12 named function bodies, but the entire compiled source epochs differ.
- Five Rust `rustc --test` cases check canonical source provider against the reference absorber away from discontinuities, true threshold ownership, photon ledgers, transparent-gas limit and identical source energy registries across q.
- Python regressions check all 108 A/B cases, string-identical physics for cache/parallel, 54.42-eV artifact, ULP false-negative, matched H/He binding threshold, positive/negative controls and source reservoir.
- Source code, original raw CSV, machine-readable summary, performance receipt and white SVG figure preserved together.

This is **not** a full evolving reionization calculation. The next constructive barrier is to implement a source-scoped dynamic H/He state with physically accountable ionization and thermal feedback under the same two photon transport lanes, retaining original photon, nuclei, threshold and heat/cooling ledgers. Then compare with an independently converged production-like BE stepper using two-dimensional time-step and energy-bin refinements. Physical detection or full CMB tau/polarization claims remain HOLD.

## Source threshold nuance

원래 Verner HeII opacity switch는 54.42 eV이고, 별도의 binding/heat bookkeeping에서는 HHeModel threshold_ev[2]=54.41776 eV를 쓴다. 이는 동일한 모델 안에서도 absorption classification threshold와 energy-bookkeeping binding energy를 명시적으로 구별해야 함을 의미한다. 이 연구에서는 두 상수 모두 원본 그대로 유지하였다. 실험의 대조군은 54.42 eV 단면적에 대한 것이며 binding threshold의 근사값을 새로운 화학 폐쇄로 제안하지 않는다.

## 최종 rustfmt 바이너리 검증

최종 소스를 rustfmt 정리 후 컴파일하여 2-worker로 216개의 A/B 레코드를 다시 생성했으며, canonical-grid-energy uncached/캐시된 기존 reference와 비교하여 runtime 필드를 제외한 모든 물리 출력 문자열이 일치했다. 최종 바이너리 SHA256 bb67e740c22383a3c5b986bff91d8e9fac454133815fcd337152507586442a45, wall-time 42.29 s였다. 이전 포맷 전 바이너리의 41.64 s 결과도 별도 기록으로 유지하며, 한 번씩 측정한 속도 지표의 신뢰구간은 제시하지 않는다. 최종 검증 결과는 results/CANONICAL_FINAL_PARALLEL2.csv에 보존한다.
