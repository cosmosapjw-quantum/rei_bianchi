# HE-ANG-SOURCE-HEX-INTAKE: independent R6 scientific review

Reviewer: `/root/source_physics`. Date: 2026-10-24 KST. Review type: source inspection and algebraic derivation. No physical provider evaluation, quadrature, old fixture, collision solver, IVP or numerical experiment was run by this reviewer.

## Decision

**The represented-coefficient Chebyshev remainder bound is valid under the explicit conditions below. The acquired Hex source is a substantive new, inspectable H1 ionization code input. It is not, by itself, a calibrated finite-mass angular provider.** The source-only unit can close at its stated intake/adapter scope after implementation review and the measured new controls. The parent HE-ANG-SOURCE physical provider gate remains pending.

This review reuses the completed HE-ANG contract, including its count2 measure, finite-mass shell, frame transformations and exact pair-correlation witness. It does not replace that theory or rerun its 32 X1 fixtures or HE-ANG controls.

## 1. Source identity and actual capabilities

The institutional source link is <https://utf.mff.cuni.cz/data/hex/hex-src.tar.gz>, reached from <https://utf.mff.cuni.cz/data/hex/index.html>. The parent retrieved 682,869 bytes with SHA256 `ebb2695ff7dbf40274d329cf706a93e040d4997254c1f6677d0ccf791a9fe6ad`. The extracted source is `Hex-src-v2.02`; the inspected files carry the MIT notice. This pin matters: current web descriptions mention newer language requirements, whereas this archive's README and `hex-ecs/src/doc.h` document C++11-era builds.

The actual path is `hex-ecs/src/amplitudes.cpp::fcheb` → `Xi_Sl1l2` coefficients → SQL `ionf` BLOBs → `hex-db/src/var/tdcs.cpp` / `ics.cpp`. The archive therefore supplies a real ionization partial-amplitude representation and the extraction code; it is more than a bibliographic claim that TDCS exists. `ionf.cpp` defines keys `(ni,li,mi,L,S,Ei,l1,l2)` and a complex coefficient BLOB. The ECS SQL writer exports incident `Ei=Etot+1/ni²` in Rydbergs. The requested H1 state is `(ni,li,mi)=(1,0,0)`.

The source archive inventory has no `.sql`, `.db`, `.sqlite` or `.h5` payload. The packaged `hex-ecs/test-run/{singlet,triplet}.dcs` files belong to the test script's elastic `1s→1s` calculation, not to an ionization TDCS dataset. The separate official SQL dataset is being catalogued by the parent; its absence or presence of `ionf` records must be determined from those bytes, not inferred from the existence of this source path. An absent table, no H1 rows or empty BLOB must not silently become a physical zero cross section.

The BLOB routines in `common/hex-arrays.h` explicitly use native endianness and raw `sizeof(T)` bytes. A portable intake must require the producer byte order, scalar precision and complex ABI; `complex128` with adjacent binary64 real/imaginary parts is a declared import convention, not a property encoded in the BLOB itself. Unknown ABI means a missing input obligation. Byte-order guessing from plausible values is not a source convention.

## 2. Chebyshev representation and safe omitted-coefficient bound

Let the stored complex coefficients be `C[0],...,C[N−1]`, with `N≥1`. For the scaled coordinate `t∈[−1,1]`, the represented polynomial is

\[
P_N(t)=\frac{C_0}{2}+\sum_{j=1}^{N-1}C_jT_j(t).
\]

This convention follows directly from both evaluation paths in `common/hex-chebyshev.h`: the constant term is `C[0]/2`. If `m` is the number of retained coefficients and `1≤m≤N`, define

\[
P_m(t)=\frac{C_0}{2}+\sum_{j=1}^{m-1}C_jT_j(t),\qquad
\tau_m=\sum_{j=m}^{N-1}\bigl(|\Re C_j|+|\Im C_j|\bigr).
\]

For real `|t|≤1`, `T_j(t)=cos(j arccos t)`, hence `|T_j(t)|≤1`. The triangle inequality and `|z|≤|Re z|+|Im z|` give

\[
|P_N(t)-P_m(t)|
\le\sum_{j=m}^{N-1}|C_j|\,|T_j(t)|
\le\sum_{j=m}^{N-1}|C_j|
\le\tau_m.
\]

This proves a uniform absolute bound for the **represented finite polynomial**, without requiring monotone coefficient decay. It covers complex coefficients, includes every omitted coefficient, and gives `τ_N=0`. Requiring `m≥1` avoids a separate half-weight rule for an omitted constant term. An implementation accepting `m=0` must instead include `|C0|/2`, not `|C0|` with an undocumented convention. Nonfinite coefficients and extrapolation outside the source interval require rejection or a different bound.

### Exact counterexample to the old local stopping rule

The original `tail(eps)` returns when the first coefficient is small relative to its running coefficient sum. It does not examine the remaining suffix. With exactly represented coefficients

\[
(C_0,C_1,C_2)=(2,0,2),
\]

the first zero causes `m=2` for every nonnegative tolerance. At the interval midpoint, `t=0`, the retained value is `P2=1` while the full value is `PN=1+2T2(0)=−1`. The omission has magnitude 2; the safe suffix bound is exactly `τ2=2`. Thus the source's local stopping criterion cannot certify the omitted remainder. This is a constructive algebraic defect witness, not an empirical result about hydrogen.

### Limits of this certificate

1. Floating-point calculation of the suffix sum may itself round downward. A mathematical `τ_m` formula is not automatically a machine-certified bound. The implementation must either compute an exact/outward-rounded upper bound for the supplied binary coefficients or explicitly carry the rounding allowance separately. Clenshaw evaluation rounding is a second, separate error.
2. This is an absolute error bound. It cannot give a relative error at a zero or near a cancellation of `P_N` without an independent lower bound on `|P_N|`.
3. The bound says nothing about coefficients beyond the stored `N`, Chebyshev interpolation/aliasing in the ECS extraction, radial/B-spline/angular truncation, quadrature, extraction radius, experimental error or model discrepancy. `fcheb` uses the same `tail` heuristic while deciding whether to extend the expansion; retaining all stored coefficients does not retroactively certify the physical fit.
4. The TDCS path divides by `k1 k2`. A uniform polynomial bound therefore does not become a uniform amplitude/TDCS bound at either zero-energy endpoint. The current source unit should certify only the polynomial intake and leave endpoint/slow-electron physical control pending.

For an explicitly interior point, one may propagate the bound constructively: if `A=Σ_a phase_a Y_a P_a/(k1k2)`, then

\[
\delta_A\le\frac{\sum_a|Y_a|\tau_a}{k_1k_2},\qquad
\bigl||A|^2-|A_m|^2\bigr|
\le2|A_m|\delta_A+\delta_A^2.
\]

This statement still excludes numerical evaluation errors and missing source-model errors. It is not needed to claim the polynomial-only unit complete.

## 3. Domain mapping is consistent

The ECS generator constructs the coefficients on `[0,kmax]` with argument `k1`, while `tdcs.cpp` reconstructs them on `[0,1]` with argument `sqrt(Eshare)`. These are exactly equivalent because

\[
k_{\max}=\sqrt{E_{\rm tot}^{\rm Ry}},\quad
k_1=k_{\max}\sqrt{s},\quad
t=2k_1/k_{\max}-1=2\sqrt{s}-1.
\]

The interval rescaling is **not a source bug**. The coefficient vector retains the same values at the same normalized coordinate. The source parameter comments do contain a separate input-order inconsistency: they advertise `(energy share,theta,phi)`, whereas both `tdcs.cpp` and `ionamp.cpp` read `(theta,phi,energy share)` from `(x,y,z)`. The adapter must name fields explicitly and use the inspected executable convention.

## 4. Source normalization and its remaining obligations

At one exact stored H1 energy, define `Ei_Ry>1`, `ki=sqrt(Ei_Ry)`, `kmax=sqrt(Ei_Ry−1)`, `k1=kmax sqrt(s)`, and `k2=kmax sqrt(1−s)`. Momenta are in inverse Bohr radii. For each spin sector, the inspected TDCS path uses

\[
F_S=\frac{1}{k_1k_2}\sum_{L,l_1,l_2}
i^{-l_1-l_2}e^{i(\sigma_{l_1}(k_1)+\sigma_{l_2}(k_2))}
\mathcal Y^{L0}_{l_1l_2}(\Omega_1,\Omega_2)P_{LSl_1l_2}(s),
\]

\[
D_S=\frac{2S+1}{4}\frac{k_1k_2}{k_i}|F_S|^2.
\]

The initial `mi=0` here is an H1 restriction, not a general replacement of the code's `mi` parameter. `ics.cpp` independently defines the database ionization cross section as

\[
\sigma_S=\frac{2S+1}{4k_i}
\sum_{L,l_1,l_2}\int_0^{\pi/4}|P_{LSl_1l_2}(\sin^2\beta)|^2\,d\beta.
\]

Here `P(s)` denotes the polynomial evaluated at `sqrt(s)` in the normalized `[0,1]` representation. This avoids confusing a Chebyshev-coordinate polynomial with an energy-share polynomial.

The two expressions are mutually consistent when `D_S` is a density with respect to **outgoing electron energy in Hartrees**, since orthonormal bipolar harmonics remove cross terms after both solid-angle integrals and

\[
k_1=k_{\max}\sin\beta,\quad
k_2=k_{\max}\cos\beta,\quad
d\varepsilon_1^{\rm Ha}=d(k_1^2/2)=k_1k_2\,d\beta.
\]

This is a derived source-internal consistency statement, not independent validation of the amplitude's absolute physical calibration. The raw TDCS output header does not identify a differential-energy unit; its output scaling multiplies only `lfactor²`. Changing the incident-energy unit does not convert the output differential-energy density. An importer must record the inferred Hartree convention and any conversion explicitly, or leave the convention unresolved pending a primary reference check. A Rydberg density is one half the Hartree density; an eV density divides the Hartree density by the Hartree-to-eV value used in that same source convention.

| Item | Evidence / interpretation | Admission requirement |
|---|---|---|
| Incident energy | SQL `Ei` in Rydbergs; H1 threshold `Ei=1` | Exact source energy and conversion |
| Energy share | `s=E1frac/(E1frac+E2frac)`; normalized amplitude argument `sqrt(s)` | Positive fractions, explicit labels, interior evaluation policy |
| Angles | Actual input `(theta,phi,Efrac)`; spherical angles converted to radians | Explicit structured fields; no ambiguous triplet import |
| Spin | Each returned sector includes `(2S+1)/4` | Sum sectors for unpolarized total; do not apply weights twice |
| Cross-section integration | `β∈[0,π/4]`, equivalently `0≤s≤1/2` | Declare half-shell indistinguishable-event counting |
| Inclusive electron marginal | Source does not directly export the HE-ANG count2 object | From each accepted event contribute both electrons; total mass `2σ` |
| Slow electron | Endpoint amplitude division is singular without limiting analysis | Endpoint/omitted-domain bound remains required |
| Approximation | Fixed nucleus and nonrelativistic dynamics | Named approximation only; no finite-mass promotion |

The half-shell integration is the unordered-event convention. Extending it to the full labelled shell without a compensating factor doubles the event integral for an exchange-symmetric density. The HE-ANG count2 marginal counts both outgoing electrons, which is a different operation from doubling the event measure. Equal energy sharing alone cannot supply an integrated energy-domain normalization.

Other static source differences remain relevant before adopting a complete physical evaluator: `ionamp.cpp` and `ionf.cpp` divide their reconstructed radial polynomial by `(k1k2)^2`, whereas `tdcs.cpp` uses one factor `k1k2`; they therefore cannot be interchanged as amplitude definitions without reconciliation. The direct ECS `computeSigmaIon_` triplet branch assigns, rather than accumulates, its angular-block integral, while the database SQL `SUM(...)` and singlet branch do accumulate. The database route avoids that particular overwrite. The TDCS multi-energy interpolation also evaluates kinematic/phase factors at requested `Ei` across stored coefficient energies, unlike `ionamp.cpp`; the current review therefore restricts the normalization comparison to exact stored energies. These observations do not invalidate coefficient decoding, but they preclude declaring all supplied extractors mutually validated.

## 5. Fixed-nucleus dynamics and finite-mass claims

The actual `hex-ecs/src/doc.h` Hamiltonian is

\[
H_\infty=-\frac{\hbar^2}{2m_e}(\nabla_1^2+\nabla_2^2)
 +\frac{e^2}{4\pi\epsilon_0}\left(-\frac1{r_1}-\frac1{r_2}+\frac1{r_{12}}\right),
\]

where the displayed source formula sets the usual atomic units. The proton is fixed and the exchange-symmetrized incoming state is built before solving. Thus the scattering amplitude is a legitimate candidate for quantum exchange in this stated approximation, but the approximation lacks finite-proton-mass internal kinetic terms.

After removing overall COM motion for finite proton mass `M`, internal coordinates relative to the proton instead give

\[
H_{\rm int}=-\frac{\hbar^2}{2\mu}(\nabla_1^2+\nabla_2^2)
-\frac{\hbar^2}{M}\nabla_1\!\cdot\!\nabla_2+V,
\qquad \mu=\frac{m_eM}{m_e+M}.
\]

The reduced mass and mass-polarization derivative change the dynamical source and threshold convention. This is not repaired by a frame boost. In a fixed-target laboratory source, appending `p_p=p_in−p1−p2` to an event with `E1+E2=E_in−I` adds the positive recoil energy `|p_p|²/(2M)` and generally violates the finite-mass shell. Reprojecting the momenta can restore conservation only by defining a new model with an explicit distribution/flux/error obligation. The existing HE-ANG finite-mass contract is the appropriate gate for that future named approximation.

No empirical angular calibration, finite-mass collision moment, kinetic closure, gas/metric evolution or physical accuracy guarantee follows from this source intake. The new finite-polynomial bound improves an identifiable numerical contract and does not consume or reset earlier source uncertainty or runtime ledgers.

## 6. Required implementation review checks

- Exact archive/dataset hashes and table inventory remain attached to the intake; missing H1 ionization data stays `SOURCE_INPUT_PENDING` rather than a numerical zero.
- Import validates H1 indices, source energy, spin, angular quantum numbers, BLOB shape, finite coefficients, explicit byte order/ABI, and coefficient-count convention. It does not manufacture a physical angular dataset.
- Tail certificate covers the entire omitted suffix and keeps polynomial truncation, floating evaluation error and physical source/model error separate.
- Manufactured witnesses are labelled algebra controls. They can verify the defect and the new bound, but not the scattering solution or its angular calibration.
- Existing X1/HE38/HE-ANG science is reused. New computation belongs only to the frozen HE-ANG-SOURCE-HEX-INTAKE ledger and its bounded invocation caps.

The algebra and approximation distinction receive **PASS**. Final implementation and evidence certification is deferred until the owned code and run receipts exist. No strong no-go conclusion is proposed.
