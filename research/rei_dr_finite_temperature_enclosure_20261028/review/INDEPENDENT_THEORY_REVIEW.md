# Independent theory review — native signed DR finite-temperature unit

Unit: `rei_dr_finite_temperature_enclosure_20261028`.
Native reviewer task identity: **`/root/current_repo_census`**.
Initial verdict fixed at **2026-10-28 11:04:18 UTC**: **R6 PASS_SCOPED_INDEPENDENT_THEORY**.

The reviewer did not author the theory, proof supplement or implementation. This is a distinct-author independent derivation and source review, with shared filesystem and prior portfolio/source-census context. It is not a blind-isolation claim. This report is fixed before reading the prepared implementation/test bodies and before any new numerical or figure output; later source-code inspection belongs in a separate addendum. The review does not use the controller's bounded CAS result as its proof.

## Target and source evidence

The admitted mathematical target is the finite real function defined using the exact binary64 images of the pinned native coefficients and constants. For each of the three retained DR rows, g_E(T)=T^(-3/2) exp(-E/T), alpha=s sum c_j g_Ej, and L=ks sum c_j E_j g_Ej on the common 100..1,000,000 K runtime domain. The conditional Maxwellian kinetic-energy interpretation is retained exactly.

`THEORY_READ_LEDGER.json` records full read ranges, bytes, SHA256 and Git-blob identities for all ten local inputs read in this initial pass. The complete reads are:

| Input | Read range | Use |
|---|---|---|
| `THEORY_AND_CONTRACT.md` | 1–146 | Complete R1–R5 argument, implementation and resource contract |
| `BINARY64_POSITIVITY_PROOF.md` | 1–19 | Source-specific exact-image positivity supplement |
| `source/atomic_coefficients.json` | 1–288 | Exact DR rows 218–280, domain 282–285 and source units |
| `source/atomic_model.json` | 1–86 | Retained species and conditional input conventions |
| `source/atomic_network.py` | 1–308 | JSON load, native parameter construction and DR number-rate formula |
| `source/recombination_moments.py` | 1–153 | Native DR rate/loss/log-derivative expressions and numerical-zero masks |
| `source/thermal_sources.py` | 1–118 | Mao RR override leaves selected DR expressions unchanged |
| `source/COPIED_SOURCE_IDENTITIES.json` | 1–32 | Source identity mapping |
| `RESOURCE_ALLOCATION.json` | 1–73 | Original frozen reservation view |
| `BUDGET_HOLD_ADDENDUM.json` | 1–94 | Actual late-debit hold superseding execution authority |

The theory SHA256 is `06c0b66e91182ec33dc97b86a6a4dab5c7ace9417a46c9adf6413ab5b4945dda`; the positivity supplement is `f0ccf92dfe8aea9fe7967dce83eff3efa6c5b5e4b9491c86b066cef2ffd44793`. The actual coefficient bytes match SHA256 `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc` and Git blob `2eba600a9d7a7359ca55f566f1b841a363a3e5c7`. The other four original source-file hashes also match the supplied source manifest.

Workflow 1.0.0 was applied: actual R6 core-transition checks and C9 independent-review requirements remain distinct from C6–C8 execution. The complete RESEARCH_POLICY, EVIDENCE_AND_HANDOFF, THEORY_LOOP and CODING_LOOP references and the local repository AGENTS policy were read. Valid earlier finite-thermal and directional evidence is preserved; none of those closed reviews is repeated here.

## Independent checks and judgment

### D1 — exact kernel extrema and signed total enclosure

Direct differentiation gives g'_E(T)=g_E(T)(E/T−3/2)/T. For E>0 it is positive before 2E/3 and negative afterward, so an interval minimum is the lesser endpoint value, while its maximum is the larger endpoint value or the interior stationary value. This establishes the exact single-term range on any positive closed interval, including a degenerate interval and a peak exactly on its boundary.

The contract's exact membership test 3a<=2E<=3b is equivalent to peak inclusion and avoids rounding a candidate before classifying it. Multiplication by a negative weight reverses the interval endpoints. Summation then encloses every total value even though extrema of different terms occur at different temperatures. The statement correctly claims enclosure rather than an exact total image.

### D2 — source-specific strict positivity and underflow distinction

For the signed rows E2>=E0 implies g_E2(T)<=g_E0(T) for every T>0. Multiplying by c2<0 reverses that comparison, yielding the stated positive two-term lower expression. The loss expression follows by replacing amplitudes by c_j E_j; no separately rounded coefficient-energy product may be substituted into the mathematical definition.

I independently checked the written decimal products by exact decimal arithmetic on paper:

- He+: 0.001417*463300 = 656.4961 and 0.00002185*888700 = 19.418095; difference637.078005, sum675.914195. The unweighted difference is0.00139515 and sum0.00143885.
- Li+: 0.00002941*634500 = 18.660645 and 0.0000007753*827100 = 0.64125063; difference18.01939437, sum19.30189563. The unweighted difference is0.0000286347 and sum0.0000301853.

These match the proof supplement. All energies are integers below2^53 and hence exact binary64 integers. Each nonzero coefficient is normal. Under the stipulated correctly rounded nearest binary64 conversion, the change in a difference is bounded by u times its positive sum, u=2^-53<10^-15. Each displayed positive margin exceeds 10^-15 times its corresponding sum. Both exact-image margins therefore remain strictly positive. The Li2+ coefficients are all positive and its energies positive.

This proves strict positivity of each represented alpha and L for every T>0, with model use limited to the stated runtime domain. On a compact interval, replacing the two positive kernels by their positive endpoint minima gives a valid uniform lower bound. Taking the maximum with the generic signed lower bound preserves validity. No floating-point evaluation or runtime Fraction check is required to close that inequality. Exact-rational serialization remains a useful pending implementation control.

Clipping a negative amplitude changes alpha upward by s|c2|g_E2 and L upward by ks|c2|E2g_E2, each strictly positive. Present-row exponential underflow to binary64 zero is consequently distinct from structural absence. This consequence follows directly from the source formula and signs, not from a sampled numerical result.

### D3 — log-temperature derivatives and uniform curvature bound

With D=T d/dT and x=E/T, Dx=−x and Dg=(x−3/2)g. A second differentiation gives D²g=[(x−3/2)²−x]g=(x²−4x+9/4)g. This matches the native first-derivative expressions for both number and loss coefficients.

The quadratic q2 has its only stationary point at x=2, with value−7/4. On a closed interval the maximum of |q2| occurs at an endpoint or at that stationary point when included. Zeros of q2 cannot create an additional positive maximum of its absolute value. The stated sum of |w_j| times independent kernel and polynomial maxima therefore bounds |D²F| uniformly. It is conservative and does not assume that term maxima coincide.

### D4 — finite log-step Taylor bound

Taylor's integral formula in ell=ln(T/K) gives the stated remainder. For h>=0, the integral of |h−u| over[0,h] is h²/2. For h<0, reverse the limits: the bound is the integral of u−h over[h,0], again h²/2. The whole segment lies in I whenever its two temperature endpoints do, since exp is monotone.

The contract correctly requires enclosure of the base value, base log derivative and log step, in addition to the analytic B2 h²/2 term. This prevents presenting a rounded linearization plus an analytic remainder as a full arithmetic enclosure. There is no derivative-approximation or small-h assumption in this bound.

### D5 — energy identity, units and source bridge

In kT(3alpha/2+Dalpha), the terms3/2 and−3/2 cancel exactly and T(E_j/T)=E_j. The remaining formula is ks sum c_j E_j g_Ej. Multiplication by k_B[J/K] and E_j[K] gives a loss coefficient J m³/s; multiplying by electron and ion number densities gives W/m³. Binding-energy transfer has a separate source owner.

`atomic_network.py` loads the JSON then converts retained DR arrays to native floating arrays; `recombination_moments.py` preserves signed amplitudes and uses the same g, first derivative and direct energy-weighted sum. `thermal_sources.py` replaces RR loss under its Mao choice and leaves these DR terms intact. The selected real function intentionally separates native parameter encoding from the full rounded evaluation path. The conditional energy closure and its lack of a separate atomic-derivative uncertainty estimate are explicit in both original source and contract.

## Findings, remaining obligations and stopping rule

**No mathematical defect was found in D1–D5 or in the exact-image positivity supplement. No theory repair is requested.** This judgment establishes the stated finite-source analytic construction and its source mapping. It does not depend on an unrun numerical test or figure.

The prior budget text in the frozen contract and allocation is a dated snapshot. The additive late-source-history evidence and `BUDGET_HOLD_ADDENDUM.json` supersede its execution authority without changing the mathematical target. The new numerical and figure jobs remain NOT_RUN. The controller's already observed bounded symbolic result is separately preserved and is not a whole-budget PASS.

Next within this review assignment: inspect the frozen implementation, independent test oracle, runner, saved-data plot repair and outer controls once, then issue a separate **C9 STATIC_ONLY_NOT_RUNTIME_ACCEPTED** addendum. C6–C8 remain NOT_RUN; later runtime admission requires actual outputs, source-identity matching and an actual figure. Original working33/88, central28/88, delta0, physical T/native25/radii=null, L4=false and global completion=null remain unchanged.

