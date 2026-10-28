# Actual-source DR finite-temperature intake

2026-10-28. Read-only physics/source intake by `/root/finite_thermal_blind_reviewer`; no numerical source evaluation, module import, CAS, IVP, new suite, or external publication. Root has narrowed the candidate to **finite-temperature enclosures and log-temperature first-order remainder bounds for the three actual signed DR rate fits and their selected DR kinetic-loss functionals**. This note confirms the source conventions and supplies inputs; root owns mathematical authoring, allocation, implementation and stage decisions.

## 1. Source match and exact defining inputs

The census refreshed PR237/PR241/VigilODE95 at 2026-10-28T10:37:59.205Z–10:37:59.788Z. The inspected refs are REI PR237 `ee6746ab172f862dddfdec63b59e5e3707b59eaa`, REI PR241 `41d2d92a186659f39cc2af60f26eba97972b6e82`, and VigilODE PR95 `36104bfc65d1fdc695c8acea383c54b50a1c4e78`. PR241's underlying BASS source is `cc602e209e7deeb511ab2a1f3b2268d55206c43c`.

At these pins, the two copies of `atomic_network.py`, `atomic_coefficients.json` and `atomic_model.json` have identical returned Git blobs **and identical local SHA256 values**. Consequently the RR/DR functional definitions and coefficient data really are shared. This does not identify the surrounding photo, temperature, state or electron-pool models.

Relevant source roots:

- **REI native:** `cosmosapjw-quantum/rei_bianchi@ee6746ab172f862dddfdec63b59e5e3707b59eaa`, `research/rei_expanded_event_consumer/blocker_closure_20261026/intake/rec119/`.
- **BASS native:** `cosmosapjw-quantum/bass@cc602e209e7deeb511ab2a1f3b2268d55206c43c`, `research/rei_hheli_compact_pilot_20261022/vendor/rec_hheli/`.
- **Thermal helper:** REI at the same pin, `research/rei_expanded_event_consumer/thermal_assimilation_20261027/vendor/rec124/rec_thermal_moments_20261022/`.

| Defining file | Git blob | SHA256 of saved source |
|---|---|---|
| Both native roots: `code/atomic_network.py` | `e3a0603176304f64b953c0b2faf898d6b75eceb5` | `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80` |
| Both native roots: `data/atomic_coefficients.json` | `2eba600a9d7a7359ca55f566f1b841a363a3e5c7` | `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc` |
| Both native roots: `data/atomic_model.json` | `73285c1585f8edca92487effe95e68448f3163b8` | `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614` |
| Thermal helper: `code/recombination_moments.py` | `4a85830af099b91549be9dae6b9dd0a0d1aae025` | `5eb740518d04dcbf123125f3d73a85fa10b48bb3bad6577cdf81459d71a390b0` |
| Thermal helper: `code/thermal_sources.py` | `f343bb0cc93cfc450b27148c8858085adb490254` | `622bc85b21d819779d98ee2a7645f51deff9a91f7a423872dbe244f5378aa769` |
| VigilODE package: `code/chemical_polynomial.py` | `06e431d01755e56d560b26d68bcd9508de128ccf` | `ff4b00b35305872f02aff88892e5b7567b5492ca14ef3feaa5e443c30e540b16` |

The VigilODE package root is `research/v8_source_chemical_jacobian_remainder_20261028/`. Exact paths, retrieval queries, all additional blobs and local SHA256 values are in `SOURCE_IDENTITIES_AND_QUERY_LEDGER.json` and `SOURCE_SHA256SUMS.txt` alongside this note. Raw responses and exact copied bodies are in `raw/` and `source/`.

## 2. DR data, domain and selected energy meaning

The actual native JSON has exactly three DR rows. Keys below are **initial** nuclear charge Z and ionic charge q, not the recombined ion label. The coefficient unit is cm³ s⁻¹ K^(3/2); E is in kelvin. Preserve all signs.

| Initial channel / key | Source coefficient lexemes c | Source E_K lexemes | Source-declared fit support |
|---|---|---|---|
| He⁺ → He⁰, `2:1` | `[0.001417, 0.0002235, -2.185e-05]` | `[463300.0, 553200.0, 888700.0]` | 10–10⁷ K |
| Li⁺ → Li⁰, `3:1` | `[2.941e-05, 6.068e-05, -7.753e-07]` | `[634500.0, 702400.0, 827100.0]` | 10–10⁷ K |
| Li²⁺ → Li⁺, `3:2` | `[0.0001451, 0.005789, 1.889e-05]` | `[852900.0, 1056000.0, 11700000.0]` | 40–4×10⁷ K |

All use source identifier `Badnell_DR_20230512`. The actual **shared runtime domain is 100 ≤ T ≤ 10⁶ K**, enforced by `AtomicNetwork.rates` and `RecombinationMoments.evaluate`; it must remain the new unit's admitted domain. The larger individual supports do not expand it. The missing DR rows for `1:1`, `2:2`, `3:3` are absent in this retained coefficient family; that is not a universal statement about omitted atomic physics. [Native JSON:218–288; native code:197–211,233–263; moment helper:55–101]

Write C for the frozen represented image of `CM3_M3 = 1e-6`, K for that of `KB_J_K = 1.380649e-23`, and let

\[
\phi_E(T)=T^{-3/2}e^{-E/T},\qquad
\alpha_{DR}(T)=C\sum_j c_j\phi_{E_j}(T),\qquad
L_{DR}(T)=KC\sum_j(c_jE_j)\phi_{E_j}(T).
\]

These are exactly the real-formula interpretations of the definitions used in `recombination_moments.py:132–142`. Alpha is in m³/s; L is in J m³/s. Multiplication by electron and ion number densities gives proper-volume power. L is **electron kinetic loss**, excluding ionization binding energy. The loss functional is the chosen signed fit moment; it is not a newly verified cross-section integral or a physical error enclosure. `ThermalSources.coefficients` changes RR under the Mao branch but leaves these DR fields intact. [Moment helper:1–15,132–153; thermal helper:65–85]

The coefficient basis frozen by root is **the exact binary64 images after native JSON→float conversion**, with scale constants treated equally explicitly. Preserve the original lexemes too. In the selected real formula, `c_j E_j` is a real product of those images; replacing it by a separately rounded product would define another coefficient basis. No claim is made that the interval encloses every rounding operation in the original NumPy callback.

## 3. Narrowing check and proposed bounded contract

With \(D=T\,d/dT=d/d\ln T\) and \(x=E/T\), written differentiation gives

\[
D\phi_E=\phi_E(x-3/2),\qquad
D^2\phi_E=\phi_E q_2(x),\qquad q_2(x)=x^2-4x+9/4.
\]

Thus root's proposed q2 agrees with the actual rate/loss formula. For positive E, phi has its sole stationary maximum at \(T=2E/3\). Its minimum on a finite positive interval is at an endpoint. For an x interval, the maximum of \(|q_2|\) is attained at its endpoints or at x=2 when included. It is legitimate to multiply separate bounds for phi and |q2|, yielding a conservative bound rather than claiming that their maxima coincide.

The proposed source-functional outputs are:

1. For each of the three frozen rows and an explicitly supplied interval `[Tlo,Thi]` inside the runtime domain, outward enclosures of the two real functions alpha and L. Each signed coefficient reverses the corresponding interval endpoints when negative. No cancellation is silently removed.
2. A conservative M for |D² alpha| or |D² L| over that interval, by summing absolute weighted kernel bounds. For a chosen T0 inside it, report the conditional first-order remainder
   \[
   |f(T)-f(T_0)-Df(T_0)\ln(T/T_0)|\le\tfrac12 M\,[\ln(T/T_0)]^2.
   \]
   Point/derivative and logarithm rounding must be handled consistently if this is returned numerically. Source inspection and the symbolic formulas alone do not verify an outward arithmetic implementation.
3. Explicit coefficient-basis, unit, domain, support and provenance labels. Physical fit discrepancy, full callback rounding, recipient state, gas heat integral, geometry work, qualified stopping law, native25 and physical radii remain unprovided/null.

This is a useful precursor to PR241's effective-rate box: its actual code constructs `b,P,Q` linearly from twelve externally supplied effective rates, but does not itself prepare a temperature-dependent rate enclosure. Converting alpha to \(n_b\alpha/H\) still requires declared positive density/clock bounds. The source-functional first unit can advance without fabricating them. It supplies no full chemical/geometry Jacobian certificate. [Chemical code:97–137,200–238]

**Underflow control is essential.** For the actual Li²⁺ row, E/T reaches 117000 at T=100 K. The real exponential remains positive while a binary64 exponential can underflow. A conservative tiny interval may include zero as a numerical lower bound, but it must preserve the present-channel flag. Do not require huge exact rational denominators or relative accuracy for this tail merely to serialize an answer under a small allocation. A negative lower bound produced by signed interval summation is also not evidence of a negative physical rate; any tightening must follow an explicit proof, not clipping.

## 4. Small discriminating validation set

These are proposed new checks, **not executed results**. Freeze their exact binary64-image or rational endpoint representation before the run. A standard-library implementation using one static three-row data read, bounded precision and no donor imports should make a <1 CPU-second command a plausible planning target. This has not been measured; root must enforce the whole-command stop and preserve any timeout rather than retrying automatically.

| Control | Concrete source choice | Distinguishes |
|---|---|---|
| Source-prescribed cold interval | All three rows on `[100,12000]` K, the old BASS prescribed thermal range | Present exponential tails versus absent channels; signed coefficients; native-domain lower endpoint |
| Saved-source local interval | All three rows on `[14907.392615960365,14923.484938308215]` K; T0=`14919.863839279506` K | A source-linked narrow interval and nonzero log-T remainder on both sides of the saved point |
| Interior kernel maximum | He⁺ with E1=463300 and interval `[E1/2,E1]` | A maximum at 2E1/3 that an endpoint-only upper bound would miss |
| q2 vertex and signed loss | Li⁺ with E1=634500 and interval `[2E1/5,2E1/3]` | x∈[3/2,5/2] includes the |q2| maximum at x=2; energy weights retain the negative third amplitude |
| Distant resonance / full domain | Li²⁺ on `[100,1000000]` K | Some stationary points are inside; the E3 stationary point is outside; the highest-energy tail must not become a support zero |

The source local interval comes from the two saved bracketing temperatures in `CALLBACK_PR237_BACKGROUND.json:3–230`. Its T0 is an adjacent-convex interpolation of saved states, with `continuum_interpolation_error=null`. It is a source calibration, not an admitted physical tube or newly evolved recipient. The complete source snapshot is preserved, including nb=10.669321142818111 m⁻³, but density is unnecessary for this narrowed scalar-coefficient unit.

Keep validation small: reuse kernel endpoints/critical points across alpha and L; at a shared high-temperature point verify the signed weighted sums against a separately arranged higher-precision expression. An explicit mutation omitting the negative term must change the He⁺/Li⁺ result; do not let a wide interval hide that control. Include one zero-width identity and rejection of an out-of-domain interval. A proof of the formulas remains distinct from spot checks of implementation. No old suite, source initialization, IVP, fitted-history replay or grid campaign is needed.

For the <1.5 CPU-second presentation target, generate a single small SVG directly from the saved new results, with interval bounds and remainder bars for the source rows. Avoid plotting-library imports and recomputation in the figure command. A few displayed source-linked points are diagnostics, not proof of all-temperature containment. This is an estimate and proposed cap, not an observed timing guarantee.

## 5. What the primary sources add, and what they do not

One new SciSpace query returned 10 records; three records describe the same Mao paper/preprint. The selected paper is Mao, Kaastra & Badnell, **The electron energy loss rate due to radiative recombination**, DOI [10.1051/0004-6361/201629708](https://doi.org/10.1051/0004-6361/201629708), arXiv [1612.01017](https://arxiv.org/abs/1612.01017). SciSpace IDs: `35l1dgy6aj`, `4wqqms7deh`, `0haere80r6dm`. Repository/index dates are not separate publications.

Its inspected Eqs. (1)–(7) define Maxwellian rate and electron-loss integrals, f=L/(kT alpha), and the temperature fit in eV; Table 2 indexes the **recombined** electron sequence. Section 4.4 treats transfer of f to other RR data as an assumption. This supports the explicit hybrid label in the native source; it supplies no universal derivative or physical-discrepancy certificate. The native implementation fixes natural logarithms; the inspected paper extraction writes `log` without independently resolving its base. No new formula/table calculation was performed here.

The [official Badnell DR documentation](https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/) confirms the signed-sum fit form, temperature/energy units, and indexing by initial electron count and initial ground/metastable level. The new unit binds the frozen project coefficients, not the current contents of the author's downloadable fit table. Exa read the paper and this official page: **one primary paper plus one official documentation page**, not ten papers read. Details and exact extraction ranges are in `ACTUAL_READ_LEDGER.md`.

No additional primary-paper search is needed for root's narrowed DR question. The full RR/Mao definitions are preserved in `RR_MAO_CONTEXT_APPENDIX.md` for context; there is **no RR enclosure claim** in the proposed unit.
