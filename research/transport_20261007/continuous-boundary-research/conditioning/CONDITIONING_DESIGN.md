# Narrow-support moment conditioning: diagnosis and remedy

Mathematical diagnosis, 2026-10-07 UTC. The V1 PARTIAL verdict and its failed 5e-13 scaled-mean gate are preserved. This note does not report a new implementation or coupled-history result.

## Actionable recommendation

For the bounded V2 prototype, keep its raw binary64 N/M/L/R interface and compute the normalized target in genuinely extended precision, including exp(-L), division, subtraction, and exact endpoint difference. A small properly implemented double-double conversion followed by one final binary64 rounding is a mathematically suitable route. More bisection, plain log/expm1 rearrangement, or FMA alone with a rounded ordinary exp(L) cannot remove the diagnosed error. Test the resulting closure against the same independent exact-binary64-input oracle and unchanged 5e-13 target.

For eventual evolving panels, storing a centered/scaled energy-excess moment directly is better conditioned and preserves information that repeated ordinary N/M serialization discards. This is a state-schema and evolution-equation change, requiring a separate reviewed migration, not a shortcut to declare V1 fixed. Source-front taper and causal support remain mandatory.

## 1. Exact-input numerical evidence

The evidence is the archived V1 closure output and independent review, with implementation and oracle in `../../continuous-boundary-prototype/`. The original diagnostic used the 30 captured closure rows, exact binary64 input interpretation, 100-digit arithmetic, and analytic exponential-family normalizers. It ran no ODE or compilation. Its measured calculation interval was 0.01986 CPU seconds and 0.01999 wall seconds; `INDEPENDENT_REVIEW.md` qualifies this as an internal calculation interval rather than a full-process receipt.

Observed maxima:

- Inverse reconstructed mean minus internally rounded target: 2.7843239934e-16.
- Rounded target minus the exact supplied binary64-input target: 1.6128157647e-9.
- Inverse reconstructed mean minus exact supplied target: 1.6128156568e-9, reproducing the existing failure.
- Ideal compensated product/subtraction but retaining rounded ordinary exp(L): 2.6935269429e-10.
- Encode the exact target as a directly rounded centered field P=N*mu, then compute P/N in binary64: 9.7354432962e-17.
- Half-ULP uncertainty in the pre-rounded physical M alone maps to a scaled-mean halfwidth up to 9.3296047563e-10.
- Difference between the original generating-beta mean and the exact stored N/M mean: up to 2.2354907201e-9.

All 30 exact stored targets are strictly interior. Thus this observed failure is not an impossibly unrealizable input or an inadequate bisection iteration count. The diagnostic distinguishes:

1. **Remediable arithmetic:** exact binary64 N/M/L/R still uniquely specify an exact target. High-precision arithmetic recovers it; the current target formula does not.
2. **Irrecoverable upstream information:** a rounded N/M pair does not specify which pre-rounded physical moment or generating beta produced it. No improved inverse algorithm can generally recover that original mean to 5e-13 on width 1e-7.

The contract correctly uses case 1. Case 2 must not be used to waive that exact-input gate or substitute the original generating beta as the answer.

## 2. Conditioning, stage by stage

For w=R-L and d=expm1(w), the exact target is

    mu = (M*exp(-L)/N - 1)/d.

Its numerator is O(w) although M*exp(-L)/N is near 1. A relative error delta in exp or the ratio becomes approximately delta/w in mu. At w about 1e-7, meeting an absolute mu target of 5e-13 requires the near-unit ratio to be known to roughly 5e-20 before cancellation, appreciably finer than ordinary binary64 precision.

The subtraction itself is not necessarily the source of fresh rounding: subtracting nearby binary64 numbers may be exact by Sterbenz's condition. It exposes errors already introduced by rounded M/N, exp(L), and their ratio. The captured stage decomposition shows those errors separately. Its final stage divides the rounded numerator by the rounded denominator in high precision; it stops before the final binary64 division rounding. The primary total-error figures independently use the recorded Rust target and therefore include that final rounding. No claim that the displayed intermediate table is an exact full replay of every Rust rounding is made. The stable expm1 denominator is already the correct form; its relative rounding error is not multiplied by 1/w after the exact ratio has been formed.

A binary64 log formulation expm1(log(M)-log(N)-L)/expm1(w) merely moves the same near-cancellation into rounded logarithms. An FMA can preserve the product/subtraction residual but cannot recover the unknown low bits of an ordinary rounded exp(L). The diagnostic quantifies that remaining obstruction.

## 3. Minimal extended-precision conversion contract

A proposed double-double target conversion is

    wd = DD(R)-DD(L),
    target_dd = ((DD(M)/DD(N))*exp_dd(-DD(L))-1)/expm1_dd(wd),
    target = round_to_binary64(target_dd),
    beta = existing_positive_closure_inverse(target).

Required safeguards:

- Use error-free two-sum/two-difference and FMA-backed two-product under their valid finite, non-overflowing domain, followed by proper double-double normalization; a pair of unnormalized floats is not automatically extended precision.
- Include exp in extended precision. A range-reduced Taylor expansion at a small argument, evaluated in double-double and followed by squaring, is a no-dependency option. Its Taylor remainder and accumulated arithmetic error must be bounded or independently checked over the declared domain. Ordinary exp plus a guessed low part is insufficient.
- Use exact endpoint difference in DD. The present narrow positive endpoints satisfy the Sterbenz condition, so their binary64 R-L is exact, but a general API cannot assume this without checking.
- Guard all domains, intermediates, subnormal/tail conditions and overflow. Reject unsupported cases explicitly. Do not quietly return a rounded target that cannot meet its error allocation.
- Verify the complete inverse mean against exact original binary64 N/M/L/R, not against target_dd rounded back into the implementation or a round-tripped M.
- A sufficient target-error certificate is an enclosure whose width and position, combined with inverse/quadrature/rounding error, remain within the same total 5e-13 allowance. Outward interval arithmetic or an explicit analytic error bound is needed to call such an enclosure rigorous; a generic epsilon multiplier is not a proof.

Because the needed ratio accuracy is around 1e-20 for the tested width, correctly implemented double-double arithmetic has ample precision in principle. This is a feasibility conclusion, not a statement that any particular DD implementation passes or has a proved global bound. Implementation acceptance requires its separate independent tests.

Fail-closed alternative: if a legacy N/M conversion lacks a reliable target-error bound or independently validated precision on the requested geometry/domain, reject it as unsupported and preserve PARTIAL. A width-only empirical cutoff is not automatically rigorous; ordinary exp has to be included in the bound. Rejection does not recover information or satisfy a requested completion guarantee.

## 4. Better-conditioned authoritative moments

Let the occupied active support be [L(s),R(s)], with the same causal-support and source-front metadata as the reviewed design. Choose anchor c(s), scale d(s)>0, and define

    phi(eta,s) = [exp(eta-c(s))-1]/d(s),
    N = integral f d eta,
    P = integral phi*f d eta.

For the moving support choice c=L and d=expm1(R-L), phi runs from 0 to 1 and

    mu = P/N,
    M = exp(L)*(N+d*P),
    U = epsilon*exp(L-s)*(N+d*P),
    0 <= P <= N.

An interior nonempty continuous closure has 0<P<N. Empty inventory, underflowed readout, and endpoint atomic limits remain distinct. Directly stored P is of the same order as N instead of being recovered by subtracting two nearly equal O(N) energy expressions. The diagnostic shows the improvement when P is rounded directly once. It does not justify deriving P from old rounded M with the same unstable formula and expecting lost information to reappear.

Keep the same positive exponential closure in y=(eta-L)/(R-L); for a newly advancing source-created front keep the interior factor (1-y). Solve its expectation of expm1(w*y)/expm1(w) against P/N. No endpoint-only trace reassignment and no new physical model are introduced.

## 5. Exact transformed evolution and face fluxes

Let q and lambda_i be the existing per-s source density and absorber rates, and define

    Q_N = integral q d eta,         Q_P = integral phi*q d eta,
    A_Ni = integral lambda_i*f d eta,
    A_Pi = integral phi*lambda_i*f d eta.

With one-sided interior traces f_L and f_R, Reynolds transport gives

    N' = Q_N - sum_i A_Ni + R'*f_R - L'*f_L,
    P' = Q_P - sum_i A_Pi + R'*phi(R)*f_R - L'*phi(L)*f_L
         - (c'+d'/d)*P - (c'/d)*N.

This follows from partial_s phi=-(c'+d'/d)*phi-c'/d at fixed eta. These basis-motion terms are mandatory. Simply replacing M by P in the old ODE would be wrong.

For c=L, d=expm1(w), w=R-L:

- Both boundaries fixed: P'=Q_P-sum A_Pi.
- HI cut moving right with L'=1 and fixed R: P'=Q_P-sum A_Pi-(N-P)/d. The number sink is -f_L. Although the lower P-face value is zero, the moving-basis term carries its effect.
- Source-created upper front moving right with R'=1 and fixed L: P'=Q_P-sum A_Pi-exp(w)*P/d, because the true front-vanishing reconstruction has f_R=0.
- For other moving-support cases use the general equation; do not combine incompatible special cases or omit an upper Reynolds term with nonzero trace.

Number face transfer F_N at eta_face has energy transfer

    F_E = epsilon*exp(eta_face-s)*F_N
        = epsilon*exp(c-s)*(1+d*phi_face)*F_N.

At the lower HI cut with c=L=s+ln(Ec), this is exactly epsilon*Ec*F_N. The same physical boundary flux remains; its bookkeeping in the transformed P equation changes because the basis moves.

Shared absorption and source energies are

    B_i = epsilon*exp(c-s)*(A_Ni+d*A_Pi),
    Q_E = epsilon*exp(c-s)*(Q_N+d*Q_P).

Taking the derivative of U=epsilon*exp(c-s)*(N+dP) and substituting both moment equations cancels every artificial c'/d' term:

    U' = Q_E - sum_i B_i - U
         + epsilon*exp(R-s)*R'*f_R
         - epsilon*exp(L-s)*L'*f_L.

Thus redshift_E'=U and the original total photon/material energy identity are unchanged. Gas heat still uses B_i-epsilon*CHI_i*A_Ni with the original species support. Compute excess-energy kernels stably on their true support rather than introducing a mean-energy replacement or reassigning residual energy.

Tiny-support factors 1/d create a genuine coordinate-conditioning/time-scale issue in differential form. Centered storage does not itself prove that a time integrator can advance to an empty cut cell. The integrated positive swept-panel transaction remains preferable near that limit, with the final N/P computed directly from positive integrals on the new support.

## 6. Source evaluation without reintroducing cancellation

For the current E^-2 source, q=K(s)*exp(-eta), K=j_total*exp(s)/(C*H). On its intersection [a,b] with the occupied panel, h=b-a and c<=a,

    Q_P = K*exp(-a)/d * [h*expm1(a-c) + h + expm1(-h)].

Both bracket contributions are nonnegative. Evaluate h+expm1(-h) through a stable series/divided-difference function for small h; its leading term is h^2/2. This expression is equivalent to [exp(-c)Q_M-Q_N]/d but avoids subtracting independently rounded large source moments. Use the same actual source representation in the state and emitted ledger. A frozen-q kernel and an exact-time q=K0*exp(s-eta) control remain distinct conventions. Here K0 is a fixed prefactor in that separate control, whereas K(s)=j_total*exp(s)/(C*H(s)) above already contains exp(s); these coefficients must not be conflated or counted twice.

Analogously, accumulate A_P directly through nonnegative phi*lambda*f samples. Forming it afterward as (exp(-c)A_M-A_N)/d recreates the very conditioning problem being removed. Source, survivor, boundary and remap contributions all need the same direct centered treatment.

## 7. Migration and compatibility implications

1. New state/version: authoritative N/P plus anchor/scale/support/front metadata. Derived ordinary M/U are output observables, not an interchangeable authoritative checkpoint. Reconstructing from rounded derived M at the next step throws away the improved information.
2. Existing N/M state: use genuinely high-precision conversion and preserve the exact meaning of the old binary64 inputs. This can repair inversion arithmetic, but cannot reconstruct the pre-rounded physical moments. Keep old failures and compatibility fixtures.
3. New moment initialization: integrate phi*f directly with positive weights or stable analytic formulas. Do not create M first and recover P by ordinary subtraction. Preserve tails or reject every unsupported underflow path.
4. Reanchoring the same unchanged distribution has the exact identity

       P_new = [exp(c_old-c_new)*d_old*P_old
                + expm1(c_old-c_new)*N]/d_new.

   This can contain cancellation when the new anchor moves right. Use compensated arithmetic with a verified bound or re-integrate the admitted reconstruction directly in the new basis. For a cut/split support, re-integrate the actual retained positive density; the two old moments alone do not describe subinterval shape.
5. Merging: choose the new anchor at or below every child anchor so transformed component contributions are nonnegative, and preserve summed N/M equivalently through the centered basis. Spectral shape bias remains independently controlled.
6. Checkpoint/API/oracle: document the new authoritative basis and exact geometry. The centered-state oracle must reconstruct M at high precision from N/P/support rather than first rounding M and then treating that rounded output as authoritative. Keep the old raw-N/M exact-input test unchanged for the compatibility conversion. This is a representation migration, not permission to weaken the same 5e-13 physical normalized-mean requirement.
7. Full coupled acceptance: no change to the existing 37 fields, species/provider/source conventions, budgets, or full-history tests. This diagnosis supplies no coupled-run evidence.

## Conclusion

The specific V1 failure is remediable target arithmetic on exact stored inputs. Its pre-rounded generating mean cannot generally be recovered, which motivates better future storage but does not excuse the current gate. DD target conversion is the smallest bounded V2 remedy; direct centered/scaled authoritative moments are the long-term representation option with the exact transformed equations above. Both require explicit admission, independent evidence, and preservation of the original failures and thresholds.
