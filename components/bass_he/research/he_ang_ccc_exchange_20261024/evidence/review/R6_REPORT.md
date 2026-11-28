# Independent R6 scientific review

**Verdict: PASS_AFTER_CORRECTION for the scoped conditional derivations in THEORY_KO.md (1)–(6).** R6-01 is closed following root's R7 correction and this same-review readback. No current blocking finding. C9 implementation acceptance remains pending actual code and execution evidence.

Reviewer: separate `/root/independent_review` agent, requested as fresh Astra reviewer; no additional reviewer spawned. This review records the requested role, not independently observable backend model metadata. Review date: 2026-10-24 UTC. One review pass plus bounded correction closure. Root-owned theory and implementation were not edited by this reviewer. An initial informal PASS message preceded the worked-example arithmetic check and missed that slip; it is superseded by this documented finding and closure.

## Inputs and method

Read the local physmath-research-loop 1.0.0 RESEARCH_POLICY.md, THEORY_LOOP.md R6, and CODING_LOOP.md C9. Read THEORY_KO.md, FROZEN_CONTRACT.json, source investigator report and original table CSV. Independently inspected rendered primary-source Bray v3 p.10 and Stelbovics p.4 and relevant extracted primary text, including Bray (21), (22), (27), section 2.5, and Stelbovics (18)–(19). Source PDFs match the recorded hashes.

Reviewed identities:

- Initial THEORY_KO.md SHA256: `3c3050d5553815ca1596a0d12e6b2247a68a7c1df3146df68c9bf8ed5d0b3634`.
- Corrected THEORY_KO.md SHA256: `911b5d39f7f0ab7e1eb130b1431ddf597fdff61c2ef80f58d883bf591c129292`.
- Final reviewed C3 clarification snapshot SHA256: `6829e9698077c4bd1d1a19e356c763310a10e25f28f7733ab0e4c7918dea9d87`.
- FROZEN_CONTRACT.json SHA256: `30a7c73b16682541e7b5e7d19d3b40357349194ca52d952af5abaefc45a5cc2b`.
- Bray PDF SHA256: `5f52f7624aab3beb7a6062d301787645d35b0a5f543c1f8b83d9de8fe8f09700`.
- Stelbovics PDF SHA256: `1ae2401f79af8e7722c4bb72bdbac854641d913e3dc32830bd258dc32597f755`.

Methods were independent symbolic derivation, dimensional reasoning, constructive witnesses, boundary and symmetry reasoning, and primary-source inspection. No physics code, test suite, numerical child, CAS, simulation, or provider solve was executed by this reviewer. Shell reads and SHA256 are document/integrity operations. Root's actual Wolfram assessment was subsequently read as correction provenance; the reviewer independently evaluates the example below without depending on the optional CAS phase endpoint output.

## Independent derivation and checks

1. **Sign and defect.** Apply the complex inner-product parallelogram law to vectors a and s b, where s is real and s²=1. It gives |a+s b|²+|a−s b|²=2(|a|²+|b|²). Equivalently the cross term in C is +2s Re(a b*) and in D is its negative. Bray's rendered (25) sets δ=a−s b; rendered (26) visibly prints subtraction of |δ|². The local correction to addition is therefore required for that pinned equation. For a=1+i and b=2−i, a+b=3+0i and a−b=−1+2i, so singlet C=9, D=5, U=7 and 14=9+5. Triplet exchanges C and D, yielding (7,5,9). The original draft's tuple (7,10,4) was incorrect. See closed finding R6-01 below.

2. **Normalized defect and symmetries.** Nonnegativity of C and D and their sum 2U gives 0≤D/(2U)≤1 for U>0. At U=0 both amplitudes vanish and η is undefined. Under swap, a+s b maps to s(a+s b), while a−s b maps to −s(a−s b); squared moduli are invariant. A common unit-modulus phase multiplies both combinations and leaves all diagnostics invariant. Constructive a=s b gives D=0, C=2U; destructive a=−s b gives C=0, D=2U. These checks cover both s signs.

3. **Weights and dimensions.** Each quadratic quantity has the source density unit; η and ratios are dimensionless. Spin weights 1/4 and 3/4 match primary Bray (21) and preserve the identity by linearity. The raw quantities are momentum-interchanged amplitudes from the same spin treatment, not distinct direct/exchange interactions; Bray (22) already contains exchange. Separate event counting must not be multiplied into this algebra. εa and εb have amplitude units, consistent with the disk radius and its squared density endpoints.

4. **Missing phase interval.** Put a=√A and b=√B exp(iφ) after removing a common phase. Re(a b*) ranges continuously from −√AB to +√AB. Multiplication by s only exchanges the endpoints. Hence the stated interval is attained in full for each spin. A=0 or B=0 gives one point; A=B>0 reaches zero and 4A. No statistical assumption follows from this deterministic interval.

5. **Complex disks.** For error disks of radii εa, εb, the Minkowski sum e_a+s e_b is the closed disk of radius r=εa+εb. For any displacement d with |d|≤r and r>0, choose e_a=εa d/r and e_b=s εb d/r to obtain that displacement inside both disks. If |z_hat|≥r the inward radial boundary realizes |z_hat|−r; if |z_hat|<r the disk contains zero. The outward radial boundary realizes |z_hat|+r. This proves both endpoints, including r=0 and z_hat=0 by direct substitution. Sharpness requires the stipulated Cartesian-product uncertainty set; an enclosing product preserves enclosure only. Positive spin weights preserve simultaneous endpoint attainability when spin uncertainty sets also form a product.

6. **Source scope and source data.** The physical equal-sharing restriction is consistent with the primary phase discussion. Pure complex identities themselves do not require equal energies. No approximation limit, integral interchange, or conservation-law derivation is used to assert (1)–(6). Stelbovics Table I visibly reports the eight transcribed 4CCC values and two BRM values, units πa0²/Ryd, total three-body energy 2 and 3 Ryd, and singlet TP energy DCS. It explicitly states factor four is already applied. The paper discusses spline interpolation producing its published table; the adapter's use of printed values does not constitute a fresh interpolation or solver. The 3 Ryd entries are nonmonotone. No full-H angular calibration, finite-mass law, empirical uncertainty, or new no-go is established or claimed.

## Finding R6-01 — CLOSED after correction

- **Object:** THEORY_KO.md section 2 explicit numerical sign counterexample.
- **Observed evidence:** For its written a=1+i, b=2−i, S=0, direct complex addition gives a+b=3, a−b=−1+2i. The true tuple is (U,C,D)=(7,9,5), whereas the document prints (7,10,4).
- **Effect:** The central symbolic identity remains correct, but the advertised exact source-sign counterexample contains incorrect arithmetic. Its printed-sign right side is 4, not the stated 6. A test fixture inheriting the claimed tuple would use a wrong oracle.
- **Minimal repair:** Preserve the written amplitudes and change the tuple to (7,9,5), corrected identity to 14=9+5, and printed-sign right side to 4. Propagate only if these numbers appear in implementation tests or source records. No scientific computation is needed for this arithmetic repair.

**Closure evidence:** Read back corrected THEORY_KO.md line 39, its correction history, and evidence/wolfram/ASSESSMENT.json. The theory now states (7,9,5), 14=9+5, and printed-sign right side 4. Root records the correction as R5-EXAMPLE-01, CORRECTED_BEFORE_EXECUTION. The independent calculation above confirms it. The initial informal reviewer PASS had missed the example arithmetic; this record preserves that review failure. General identities, conventions, and budgets are unchanged. C9 will check that the implementation's example uses the corrected values.

**Final R6 verdict: PASS_AFTER_CORRECTION.** Optional Wolfram phase-endpoint output lacks its needed nonnegative assumptions and is recorded NOT_ADOPTED; the constructive nonnegative-input derivation in this report supplies the mathematical phase-range check. C9 will separately check actual implementation and outcomes. The original full H1 joint payload remains SOURCE_INPUT_PENDING.

### C3 clarification readback

The final theory snapshot adds the positive-denominator identity (√A−√B)²=(A−B)²/(√A+√B)² for A+B>0, and treats A=B=0 separately. This follows by multiplying √A−√B by √A+√B and is correct for nonnegative inputs. Evaluating it numerically still requires scaling to avoid intermediate overflow/underflow. The new text correctly distinguishes exact real-arithmetic range sharpness from approximate binary64 endpoints at the unchanged 5e-13 scaled criterion; it explicitly does not claim a directed-rounding certified enclosure. This clarification passes R6. C9 will examine actual extreme-scale representation, near cancellation, and the claimed scope of numeric fidelity using implementation and actual evidence.
