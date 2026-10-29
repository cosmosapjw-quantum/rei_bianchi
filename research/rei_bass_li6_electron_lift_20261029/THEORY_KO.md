# REI↔BASS: source-locked Li6 isotope-equivalence lift and electron-feedback Jacobian

**2026-10-29 · `REI_BASS_LI6_ELECTRON_LIFT_20261029`**. Parent [REI PR265](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/265) HEAD `9b0b97aadeebf368802f865c10eb8b633f2726e4`. Original working DAG **33/88**, central **28/88**, physical delta **0**. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`. This is a conditional exact result **inside the BASS atomic 21-state RHS**, not a source-identification theorem between the BASS and REI pilots.

## 1. Actual source and conventions

Byte-qualified original BASS PR234 source: `atomic_network.py` SHA256 `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, `atomic_model.json` SHA256 `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614`. Source formula from `AtomicNetwork.evaluate` (not a fitted derivative) is

\[
 \frac{\mathrm dY}{\mathrm dt}=F_{21}(Y;t)=\big[G_0(t)+D+n_b(t)(q_{21}^{\mathsf T}Y)G_{\mathrm{ne}}(t)\big]Y,
 \quad n_e=n_b q_{21}^{\mathsf T}Y.
\]

Here `Y_i=n_i/n_b`, dimensionless, `n_b` is proper baryon number density in m\(^{-3}\); `G_0,D` have units s\(^{-1}\), `G_ne` has units m\(^3\) s\(^{-1}\). The source itself computes the Jacobian `J21=G0+D+n_e Gne+n_b(Gne Y)q21^T`. At `x=ln(a/a_ref)` the derivative is `Y_x=F21/H` when the same positive H has units s\(^{-1}\). Default signature `(-,+,+,+)`.

Original isotopic block indices are `Li6=(13,14,15,16)` and `Li7=(17,18,19,20)` in the zero-based 21-vector. Both are electronic Z=3,q=0,1,2,3, and the source computes photoabsorption/recombination coefficients only from `Z,q`, temperature, and the same prescribed radiation. Its explicit decay matrix has transitions `n→H1+`, `T0→He3+`, `T+→He3++` but **none acting on Li6/Li7**. Source flags exclude lithium nuclear reactions and externally supplied Li6/Li7 conversions. These are *source-contract facts*.

BASS original two Li inventories are **positive**: `inventory_number_ratios_to_H1['Li6']=1e-14` and `['Li7']=5e-10`; both begin singly ionized. Source owner uses binary64 `math.fsum` to normalize each isotope. Under the actual represented-real convention, let `nu6=Fraction.from_float(float(1e-14/norm))`, `nu7=Fraction.from_float(float(5e-10/norm))` and `gamma=nu6/nu7`. Ideal-decimal gamma is 1/50000; the exact represented-real gamma differs slightly. The latter, rather than a rounded shortcut, is used below.

REI selected seven 17-state `ON_refined` values (source JSON SHA256 `7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77`) are **a different, uncalibrated pilot**, with nonzero T, different isotope inventories, and a different UVB photon-source history. They are not a solution of BASS's photo/recombination family. No physical `nHref/nb`, `H`, `K`, shared initial conditions or full REI Jacobian is bound.

## 2. Exact invariant isotope-equality submanifold

Define retained indices `I=(0,...,12,17,...,20)`, projection `P:R^21→R^17` and lifting `E_gamma:R^17→R^21` by retaining all non-Li6 groups and setting

\[
 (E_\gamma y)_{{}^6\mathrm{Li},q}=\gamma y_{{}^7\mathrm{Li},q}, \qquad
 (E_\gamma y)_{I}=y,\qquad PE_\gamma=I_{17}.
\]

`gamma>0` is **time-independent** because the BASS Li isotope nuclear totals are conserved by its declared active reactions. The ratio `Y6,q/nu6=Y7,q/nu7` holds at the owner pilot initial datum (both entirely Li+) and defines the image of `E_gamma`. The two isotope blocks obey the *same* linear homogeneous charge-redistribution equation

\[
 \dot Y_6=M_{\rm Li}(t,n_e)Y_6,\quad
 \dot Y_7=M_{\rm Li}(t,n_e)Y_7,
\]

where `M_Li=G0_Li+n_e Gne_Li`. The common electron density may depend nonlinearly on **all** 21 populations; both blocks nevertheless experience exactly the same operator on any given trajectory. Thus `d(Y6-gamma Y7)/dt=M_Li(Y6-gamma Y7)`, proving invariance for identical initial charge fractions. The result holds despite full electron-feedback nonlinearity and does not require another IVP. Nonzero T or neutron species elsewhere do not by themselves invalidate this **Li** identity, although T→He3 weak sources can invalidate a separate He3/He4 equality.

Set `f17(y;t)=P F21(E_gamma y;t)`. Since no active Li nuclear/decay channel exists and the Li electronic rates coincide,

\[
 \boxed{F_{21}(E_\gamma y;t)=E_\gamma f_{17}(y;t)},\qquad
 \boxed{J_{21}(E_\gamma y;t)E_\gamma=E_\gamma J_{17}(y;t)}
\]

follow identically. The second identity is obtained by differentiating the first with respect to `y`, not by assuming that the pointwise output electron rate is a trajectory sensitivity. `J17=P J21(Ey) E`. This gives a source-structured exact **BASS** 17-dimensional reduction on the specified submanifold. It is not the original REI model and does not automatically equal BASS compact33/reduced30.

## 3. Electron covector and the correction missing from a naive REI-17 contraction

Let `q17` be the charge row for the retained species and let `q7=(0,1,2,3)` act on the retained Li7 block. Then

\[
 q_{21}^{\mathsf T}E_\gamma y
 =\underbrace{q_{17}^{\mathsf T}y}_{\text{naive retained electron pool}}
 +\underbrace{\gamma q_7^{\mathsf T}y_{Li7}}_{\eta_6(y)},
 \quad \delta q\equiv \gamma(0,\dots,0,0,1,2,3)^{\mathsf T}.
\]

The true source-qualified condensed BASS RHS is `f17=(A+n_b[(q17+deltaq)^T y] R)y`, with **`A=P(G0+D)E` and `R=P Gne E`**, all evaluated at the same external time and rate input. Comparing against a **formal** 17-state model with the *same* matrices but the Li6 electron term artificially omitted,

\[
 \Delta f=n_b(\delta q^{\mathsf T}y)Ry,\quad
 \boxed{\Delta J=n_b\left[(\delta q^{\mathsf T}y)R+(Ry)\delta q^{\mathsf T}\right]}.
\]

The second term of `Delta J` is rank-one, whereas the first generally is not. Therefore the **whole correction need not be rank-one**. This distinction is specifically tested. All rates in `R` are in m³/s; the resulting `Delta f` and `Delta J` have dimensions s\(^{-1}\) acting on dimensionless populations. The positive Li6 charge bound `0<=eta6<=3 nu6` is **sharp on the Li isotope simplex** (all neutral vs all triply ionized).

With induced matrix 1-norm and `deltaq` supported on Li7 with maximum entry `3 gamma`, an immediately valid source-conditional bound is

\[
 \|\Delta J\|_1\le n_b\{3\nu_6\|R\|_1+3\gamma\|Ry\|_1\}.
\]

This is not a numerical physical error certificate: the source-owner `n_b(t),R(t),y(t)` and numerical error enclosures have not been bound. At any *supplied* BASS state the difference in the positive cumulative Thomson source row is **conditionally** `Delta(tau_x)=(K n_b/H)eta6` with `0<=Delta(tau_x)<=3 K n_b nu6/H`, assuming `K,n_b,H>0`. It is not an actual integrated optical depth, CMB response or parameter tangent.

Source-derived initial numbers: `nu6≈7.549543987593138e-15` per baryon, `3 nu6≈2.2648631962779414e-14`, and the initial Li6 contribution to the *initial BASS pilot* electron pool is approximately `4.99986250353116e-11` of the total. These ratios are unrelated to the earlier PR265 cross-pilot inventory minimax 0.4943–0.5186%; the two refer to distinct questions.

## 4. Exact counterexamples and clock transport

If the Li6 photo rate at `q=0` is changed by `epsilon` while Li7 remains at the original rate, then the lift residual has explicit nonzero entries `(-epsilon*gamma*yLi7,0, +epsilon*gamma*yLi7,0)` in the Li6 charge block (positions 13 and 14). This local counterexample shows the precise **premise** of isotope electronic equality; it is not a general physical impossibility theorem. In the original BASS weak decay, positive T0 feeds He3+ but not He4+, so the analogous He3/He4 equal-fraction condition does **not** generically survive when T is present.

To express a BASS per-baryon retained state as a REI per-Href state, write `Y_ret=rho(x)y_REI`, `rho=nHref/n_b>0`. Differentiating gives

\[
 y_{\mathrm{REI},x}=\rho^{-1}Y_{\mathrm{ret},x}-(\rho_x/\rho)y_{\mathrm{REI}}.
\]

If the ratio is unknown or parameter dependent, this term cannot be removed. More fundamentally, the actual REI source contains distinct nuclear/CR/thermal/fast/injection events and original prescribed-bath assumptions. A BASS internal exact invariant does **not** prove cross-repository dynamic equivalence. The original pilot inventory mismatch, F4/L4 hold and `NO_MORE_IVPs` remain effective.

## 5. Validation and literature

- **Source-backed derivation:** original `AtomicNetwork.evaluate` code implements the RHS and Jacobian shown above; photo and recombination rates are indexed by `(Z,q)`; decay block n/T only. Exact SHA verification is performed before the new code evaluates any snapshot.
- **Actual current-turn code execution:** Python unittest `30/30 PASS` with 22 exact Fraction random 21→17 RHS/Jacobian intertwining cases, nonnegative Li charges, explicit isotope-rate mismatch, ion totals, negative source-integrity check, finite-difference quadratic `Delta J` check. These exercises use **synthetic rational photo/recombination rate coefficients** attached to the authentic source *structure*, not the BASS native rate tables. C++20 independent seven-row `7/7 PASS` on the source-pinned REI snapshots with **counterfactual** Li6 recovery and no IVP.
- **Wolfram actual symbolic test:** a two-charge, two-isotope nonlinear electron-feedback toy has `F(Ey)-E f(y)={0,0,0,0}` and `J(Ey)E-E j(y)=0_(4x2)`; setting a Li6-specific photo-rate perturbation produces `(-epsilon gamma u,+epsilon gamma u)` in the Li6 block. This verifies the conditional mechanism but is not a different-author R6/C9 review.
- **Theory context:** Ovchinnikov et al., *CLUE: exact maximal reduction of kinetic models by constrained lumping of differential equations*, *Bioinformatics* 37 (2021), DOI [10.1093/bioinformatics/btab010](https://doi.org/10.1093/bioinformatics/btab010), supplies the Jacobian-invariant-subspace criterion for exact polynomial ODE lumping. Eilertsen et al., *Lumping of reaction networks: Generic and critical parameters* (arXiv [2606.28895](https://arxiv.org/abs/2606.28895), 2026-06-27), clarifies generic versus critical rate-parameter regimes. Neither paper proves this source-specific Li6 theorem without the above extraction and proof.

**Admission:** conditional BASS-internal Li6 lift **DERIVED + SYMBOLIC_CHECKED + IMPLEMENTATION_VERIFIED_SCOPED**; original REI↔BASS full chemistry/physical tau still `UNRESOLVED`, native source full-rate execution `NOT_RUN`, distinct-author R6/C9 `NOT_RUN`, physical DAG delta0.
