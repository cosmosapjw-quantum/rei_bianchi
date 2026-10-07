# Independent conditioning-design review

2026-10-07 UTC. Mathematical and source review. No new numerical run or implementation was performed for this review. Line numbers and the diagnostic file names below refer to the archived originals.

## Verdict

**CONFIRMED as a bounded mathematical diagnosis and remedy design.** The distinction between exact supplied binary64 moments and unknown pre-rounded physical moments is correct. The transformed equations, boundary-energy cancellation, stable source integral, and migration requirements are algebraically consistent. Proper double-double target conversion is feasible for the tested geometry; this is not a verified implementation or a universal precision certificate.

The existing V1 PARTIAL result and failed 5e-13 exact-input gate remain unchanged. This review makes no claim about V2 results, complete tail admission, integrated evolving-panel performance, or production readiness. Two minor notation/reporting clarifications found during review were incorporated and inspected below; remaining evidence qualifications are explicit.

## Findings and traceability

### 1. Exact-input arithmetic versus missing upstream information: confirmed

`CONDITIONING_DESIGN.md:36–44`, `diagnose.py:8–24`, V1 `src/primitives.rs:348–381`, and the inverse section of V1 `oracle.py` use the same exact target:

    mu = (M exp(-L)/N - 1)/expm1(R-L).

The diagnostic deliberately converts each CSV scalar through binary64 before converting it to 100-digit arithmetic. This preserves the oracle's authoritative-input convention. Its analytic normalizers are correct:

    Z_ordinary(beta) = (exp(beta)-1)/beta,
    Z_front(beta) = (exp(beta)-1-beta)/beta^2,
    E[exp(w y)] = Z(beta+w)/Z(beta).

The removable beta=0 limits are correctly supplied. Thus this analytic diagnostic does not merely repeat the implementation's Gauss64 root evaluation. The reported root-to-recorded-target error (2.7843e-16 maximum) and recorded-target-to-exact-input error (1.6128e-9 maximum) consistently identify target arithmetic as the dominant tested failure. The quoted maximum inverse-to-exact-input discrepancy agrees with the retained independent V1 review.

Holding N,L,R fixed, the derivative d mu/dM is exp(-L)/(N expm1(w)). The image of a half-ULP rounding interval in M therefore has exactly the diagnostic's scaled halfwidth. The approximately 9.33e-10 narrow-case halfwidth already exceeds 5e-13 by orders of magnitude. These intervals stay inside the realizable mean range for the supplied fixtures. This proves non-identifiability of the pre-rounded mean from the stored pair; it does not weaken the exact-input reconstruction requirement. A generating-beta comparison is illustrative, not the oracle target.

Interior means are realizable by the unrestricted positive exponential families because the mean of a strictly increasing function of y increases strictly with beta and tends to its endpoint limits. Interior status alone does not prove admission by a finite beta bracket. The tested roots are near beta values between -64 and 64, well within the existing +/-128 bracket; a future API must retain its bracket and conditioning checks.

### 2. Double-double remedy: confirmed feasibility, unverified execution

`CONDITIONING_DESIGN.md:46–66` correctly includes extended-precision exponential evaluation, division, cancellation, and endpoint geometry. At w approximately 1e-7, an absolute target error of 5e-13 requires near-unit ratio error of approximately 5e-20 before cancellation. Ordinary binary64 exp/division errors are too large; ideal product/subtraction compensation that retains the rounded exp(L) leaves the reported approximately 2.69e-10 residual. More bisection cannot repair a wrong target.

Normalized double-double arithmetic has enough precision in principle for these finite normal fixtures. Its exponential approximation, range reduction, accumulated error, division, endpoint calculation, and final rounding still need a domain-specific bound or independent validation. FMA-backed two-product is not unconditionally error-free across overflow or underflow. A mean enclosure must leave room for inverse/quadrature and final-rounding errors within the original total tolerance. The design explicitly preserves these requirements and does not mistake a generic epsilon multiplier for a proof.

### 3. Centered moment and moving-boundary equations: confirmed

For phi=(exp(eta-c)-1)/d at fixed eta,

    partial_s phi = -c' exp(eta-c)/d - (d'/d) phi
                  = -(c'+d'/d) phi - c'/d.

Combining this identity with Reynolds transport proves both equations at `CONDITIONING_DESIGN.md:95–101`, including both moving-face terms. For c=L and d=exp(R-L)-1:

- L'=1, R'=0 gives d'=-(1+d), so the basis term is -(N-P)/d. The lower P-face term vanishes because phi(L)=0, while N retains the lower loss -f_L.
- L'=0, R'=1 gives d'=1+d, so the basis term is -exp(w)P/d. The upper face term vanishes only for a genuine interior front trace f_R=0.

The closure's interior factor (1-y) provides that front trace; merely redefining its value at y=1 would not. The stated causal support/front metadata remains necessary. The small-d coefficients also show why a better state representation does not itself solve near-empty-cell time integration.

### 4. Energy conservation and boundary ownership: confirmed

Set S=N+dP. Substitution of the two moment equations gives

    S' = Q_N+d Q_P - sum_i(A_Ni+d A_Pi)
         + exp(R-c) R' f_R - exp(L-c) L' f_L - c' S.

Since U=epsilon exp(c-s) S, the c' terms cancel and differentiation gives exactly the reported -U redshift term and physical boundary energies. In particular, the HI-cut number flux carries epsilon E_c per photon when L=s+ln(E_c). Neither basis motion nor moment conversion permits an energy-ledger repair, a mean-energy absorption replacement, or a change to species support or gas heating. The proposed expressions for B_i and Q_E use the same shared count/centered-energy integrals.

### 5. E^-2 source formula: confirmed, with a notation clarification

At fixed s, integrating q=K(s) exp(-eta) directly on [a,b] gives

    Q_P = K(s)/d [exp(-c) h - exp(-a)(1-exp(-h))]
        = K(s) exp(-a)/d [h expm1(a-c) + h + expm1(-h)].

For h>=0 and a>=c, both h expm1(a-c) and h+exp(-h)-1 are nonnegative. The latter is h^2/2-h^3/6+..., so a direct floating-point evaluation of h+expm1(-h) would still cancel; the explicitly required stable series/divided-difference evaluation is essential. Direct nonnegative accumulation of A_P and source/survivor/remap centered moments is also necessary.

**Clarification corrected during review:** The initially reviewed `CONDITIONING_DESIGN.md:134` defined K(s)=j_total exp(s)/(C H), whereas line 138 reused K in the separate exact-time convention q=K exp(s-eta). This could count exp(s) twice if read literally. The corrected design uses K0 for the separate fixed prefactor and explicitly distinguishes it from K(s). The corrected text was inspected. This clarification does not alter the fixed-s integral above.

### 6. State migration and oracle conventions: confirmed

The identity at `CONDITIONING_DESIGN.md:147–153` follows by substituting exp(eta-c_new)=exp(c_old-c_new)[1+d_old phi_old]. It is valid for the same unchanged distribution. Cutting a support requires integrating the retained distribution; moments alone do not determine subinterval content without an admitted closure. Moving an anchor right can cancel in the reanchoring identity. Merging with a new anchor at or below all child anchors avoids that sign cancellation when each child P is nonnegative.

The N/P state, geometry, front metadata and checkpoint version must be authoritative together. Rounding a derived M and using it as the next authoritative moment recreates the original loss. The new oracle must interpret exact supplied N/P and geometry, evaluate the corresponding physical moments at sufficient precision, and independently integrate the reconstructed shape. The old exact-N/M conversion test remains separate and unchanged. Empty, atomic-limit and unresolved-tail states remain distinct.

The statement that P is of the same order as N is appropriate for bounded interior means, not uniformly as P/N tends to zero. The design's separate endpoint/tail admission requirements are therefore important rather than optional.

## Evidence qualifications

- The diagnostic's stage sequence ends with a high-precision division by a rounded denominator (`diagnose.py:16`), before the final binary64 division rounding. Therefore its last stage should not be read as bit-for-bit reproduction of the recorded Rust target. The principal comparison correctly uses T read from the captured output, so the main diagnosis is unaffected. The corrected original includes this qualification at line 42, and the text was inspected. Python math functions are also not by themselves a guarantee of identical Rust libm intermediate values.
- The 100-digit calculation and old 80-digit integral oracle are high-precision numerical evidence, not outward-rounded interval certificates. No new numerical rerun or convergence test was conducted for this review.
- The reported diagnostic CPU/wall fields begin after imports and end before JSON writing; they describe the measured calculation interval, not a complete external process receipt. The source sets CPU/address-space limits, while the recorded command supplies the wall timeout. This reviewer did not independently witness that earlier execution. This qualification does not challenge the mathematical findings.
- All four input hashes recorded in DIAGNOSTICS.json were independently recomputed with SHA-256 and matched. V1 oracle.py also matches the identity retained in its independent review.

## Archived original reviewed artifact identities

These SHA-256 values identify archived originals inspected in this review, not the relocated publication bytes. Line references likewise identify those originals.

- CONDITIONING_DESIGN.md, archived final corrected text bound to this verdict: `c6ff53341d921ddadaedfb1375b49b8771a08543d4668c81a029d2897d374d97`
- CONDITIONING_DESIGN.md, initial reviewed version before the two clarifications: `6d6100408504373bd2bac9888a9593549f517ed6bdcb0b42c70ce1cc08314a15`
- CONTRACT.md: `aadad811bdec3f8ed0f436fbc3c7ac7e18985a0637a9299a3a9411189bfc0927`
- DIAGNOSTICS.json: `271433b92c278472f4a67d0f720605a7fd67d71b6b212b348e96960ea0df4b8b`
- diagnose.py: `02b74bbfdd3718fd19619d632851255474162a036f1c196640b3535bea8a26e5`

The mathematical causes and remedy/migration specification have been independently checked. Numerical implementation acceptance requires separate bounded evidence. No failed V1 gate or broader coupled acceptance requirement is waived.
