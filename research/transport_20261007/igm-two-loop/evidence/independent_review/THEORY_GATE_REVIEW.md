# Independent theory gate: IGM continuous boundary and positive-panel bridge

Review date: 2026-10-07. Scope: read-only independent mathematical review before the new implementation. This is a derived contract and audit of the supplied source, not an execution receipt. The source intake identifies IGM head `39c39eab` and the transport scientific source `a9aea514`; the full identities and byte hashes are owned by `intake/igm/SOURCE_MANIFEST.json`.

## Decision

The existing design correctly distinguishes (i) a continuous swept-boundary measure from persistent photon nodes, (ii) owner quadrature from moment-conserving reconstruction, and (iii) authoritative positive tails from exact emptiness. Implementing those distinctions is necessary to remove the long-window export staircase. Connecting the current normal-only V2 kernel to midpoint gas stages is insufficient by itself.

There are three independent blockers:

1. **Nonzero export:** the inherited short window ends at Delta ln(a)=2e-4; even the proposed four-base-window end at 8e-4 precedes the first source export by a factor of nine. For the source minimum 13.7 eV and tracking cutoff 13.6 eV, first export is Delta ln(a)=ln(13.7/13.6)=0.007326040092. Exact zero outflow in shorter runs cannot test the staircase defect.
2. **Tail arithmetic and shape:** the supplied physical frozen-opacity witness reaches zero binary64 readout before the third 2e-4 endpoint. A source-off wake also has a logarithmic slope of order 1.37e6 per eta; its fitted panel beta can exceed the V2 bracket +/-128. Amplitude coverage and closure-shape coverage are separate.
3. **Projection feedback:** preserving number and energy leaves photo-rate and heating functionals undetermined. A successful one-step owner comparison neither certifies repeated projection nor certifies coupled gas histories.

Recommended ordering: first close a bounded continuous-boundary/tail primitive with true nonzero export and fail-closed admission; then derive and test moment-based observable envelopes or perform an explicitly bounded gas-feedback extension. Do not introduce anisotropic geometry before these FLRW spectral errors are separated. The existing production lower-boundary export remains open until the new primitive is actually connected and its long-window 37-field reference comparison passes.

## 1. Definitions, dimensions and balance identities

Let s=ln(a), eta=s+ln(E/eV), epsilon=1 eV expressed in erg, and f(s,eta) denote photons per hydrogen nucleus per d eta. Hydrogen nuclei conservation has already absorbed the physical a^-3 dilution into this normalization. At fixed eta in FLRW, dE/ds=-E. For a frozen segment with source q and species opacities lambda_i,

    partial_s f = q - lambda f,    lambda = sum_i lambda_i,
    lambda_i = c n_i sigma_i(E) / H.

The lambda_i are dimensionless per s; f and q have photon/H/eta and photon/H/eta/s units respectively. Here n_i are proper absorber number densities. The diagnostic photoionization rate per absorber is

    Gamma_i = c n_H integral sigma_i(E) f d eta,

with units s^-1. It remains well defined at zero abundance of absorber i and must not be reconstructed by dividing an absorbed-count owner by that abundance.

For a segment of width h beginning at physical energy E_a, define

    J(k,h) = integral_0^h exp(-k u) du,
    f_1 = f_0 exp(-lambda h) + q J(lambda,h),
    I_N = integral_0^h f(u) du,
    I_E = integral_0^h exp(-u) f(u) du.

The shared owners are

    A_i = lambda_i I_N,
    B_i = epsilon E_a lambda_i I_E,
    Q_N = q h,
    Q_E = epsilon E_a q J(1,h),
    R_E = epsilon E_a I_E,
    U_1 = epsilon E_a exp(-h) f_1.

Consequently, in exact arithmetic,

    f_1 + sum_i A_i = f_0 + Q_N,
    U_1 + sum_i B_i + R_E = epsilon E_a f_0 + Q_E.

These are independent local identities, not definitions of a missing owner by residual. Useful oracle formulas are

    I_N = f_0 J(lambda,h) + q [h-J(lambda,h)]/lambda,
    I_E = f_0 J(lambda+1,h)
          + q [J(1,h)-J(lambda+1,h)]/lambda.

Both expressions require their analytic lambda=0 limits or a positive integral/series evaluation: I_N=f_0 h+q h^2/2, I_E=f_0 J(1,h)+q integral_0^h u exp(-u)du. A formula that directly subtracts nearly equal J values is not an independent stable implementation at small lambda h. The arbitrary-precision oracle can integrate the explicit f(u) positively instead.

If eta reaches the HI cutoff at tau=eta-ln(E_c/eV), terminate that characteristic at tau, transfer its surviving f to out_N, and transfer epsilon E_c f to out_E. There is no continuing active stock. Source entry, source exit, and species cutoff events divide the same physical history before any owner is evaluated.

For b(s)=s+ln(E_c/eV), the continuum active inventory obeys

    dN/ds = Q_N' - sum_i A_i' - f(s,b(s)^+),
    dU/ds = Q_E' - sum_i B_i' - U - epsilon E_c f(s,b(s)^+).

The last term is the lower moving-face flux, while U is expansion work. Integrating the swept strip with its characteristic exit time realizes these terms continuously. Releasing whole persistent node weights produces numerical atoms and a staircase that is not part of the smooth physical measure.

## 2. Coupled H/He ownership

Let f_He=n_He/n_H, and x_HeII, x_HeIII be fractions relative to all helium nuclei. Then the gas consumes the same radiative owners:

    Delta x_HII(photo) = A_HI,
    Delta x_HeII(photo) = (A_HeI-A_HeII)/f_He,
    Delta x_HeIII(photo) = A_HeII/f_He,
    Delta w(photo) = sum_i [B_i-epsilon chi_i A_i].

The binding inventory is epsilon[chi_H x_HII + f_He chi_HeI x_HeII + f_He(chi_HeI+chi_HeII)x_HeIII]. Its gain exactly cancels the threshold part removed from the thermal gain. Thresholds chi_i used in gas binding/heating are not interchangeable with the cross-section cutoff values. The midpoint nonphoto work, escape, and CMB reservoir remain separate owners with their inherited signs.

At every nonlinear trial, opacity and radiative owners must be recomputed from the same trial affine gas path. Reusing owners from a previous gas endpoint may solve a different residual while preserving an internally constructed ledger. The frozen endpoint closure/projection must occur only after the gas root is accepted. A projection failure rejects the whole candidate; it cannot leave an accepted gas update with stale radiation.

## 3. Positive moments, source fronts and restrictions

For each occupied panel [L,R], authoritative moments are N=integral f d eta and M=integral exp(eta) f d eta; U=epsilon exp(-s)M. Nonzero smooth positive density requires exp(L)<M/N<exp(R). Endpoint equality describes an atom, not an ordinary smooth closure. Geometry-empty and exported supports have exact zero measure; finite-log tails do not.

A right-front closure must taper over its interior, f proportional to (1-y)exp(beta y), y=(eta-L)/(R-L). Assigning only the endpoint value zero does not establish the trace or a continuous boundary flux. Restricting such a panel to a left child does not introduce a new zero at the child's right endpoint. The source-on lower edge also has zero trace in the exact initially empty solution, although an ordinary closure can approximate it with a disclosed shape error.

On each temporary subinterval J, the physical one-point moment rule has weight n_J and energy coordinate eta_J=ln(m_J/n_J). It integrates 1 and exp(eta) exactly in real arithmetic, before evaluating owners. These points are ephemeral quadrature devices. They must be rebuilt after continuous cuts; they are not persistent photons whose entire weight waits for a cutoff crossing.

Stock quadrature weights carry photon/H units; source geometric quadrature weights carry eta units. The two must be represented by distinguishable interfaces. Forming an exact continuum source total and then placing it into a segment-frozen source ledger changes the numerical source definition and is not a permitted budget repair.

## 4. Tail admission

For the exponential segment, authoritative log density evolves as

    log f_1 = logaddexp(log f_0-lambda h, log q+log J(lambda,h)).

In particular, source-free tails use -lambda h, not the backward-Euler -log1p(lambda h). A raw f64 value of zero does not establish emptiness. Every positive weighted contribution, energy owner, species owner, and export requires retained scale/log provenance or a checked dimensional loss bound. One normal aggregate cannot justify silently dropping a tiny component.

A shared binary exponent with normal N/M mantissas preserves the shape ratio better than subtracting two large negative log moments. It still requires independently tested summation and conversion; finite precision can lose a physically significant small addend relative to a much larger common scale. Normalization and moment-realizability admission remain independent of amplitude admission. Unsupported beta or arbitrarily narrow event slivers must reject or undergo a declared compatible moment-preserving merge; no floor or missing-measure deletion is permitted.

The conservative budget gate is |number residual|+loss_N <= original allowance and |energy residual|+loss_E <= original allowance. This strengthens rather than relaxes the original test. Quadrature and projection errors are not numerical-underflow losses and must appear separately.

## 5. Mathematically useful second-loop extension: observable envelopes

Consider any positive spectral measure dnu=dN on physical energy support [a,b], with a>0, total N>0, and mean mu=U/(epsilon N). For a convex function g,

    N g(mu) <= integral g(E) dnu
      <= N [(b-mu)g(a)+(mu-a)g(b)]/(b-a).

The lower inequality is Jensen's inequality. The upper inequality follows by integrating the pointwise secant-line upper bound for a convex graph. It uses only the two authoritative moments and support, and therefore holds for both the incoming spectrum and every positive reconstruction with the same moments.

For the explicit power-law control g(E)=E^-3, g''=12 E^-5>0, the bounds are

    N mu^-3 <= integral E^-3 dN
      <= N [(b-mu)a^-3+(mu-a)b^-3]/(b-a).

They show mathematically why N/U conservation does not certify Gamma. The gap is a positive resolution indicator, and any two spectra sharing these moments differ in this observable by at most the gap. In the narrow-panel limit the gap is O((b-a)^2); it need not vanish merely because the nonlinear gas residual or photon/energy ledger vanishes. Endpoint atoms attain the upper bound, while a point mass at mu attains the lower bound. Smooth positive densities approach those extrema but need not attain them.

For an arbitrary twice differentiable physical kernel g with |g''|<=K on a threshold-free panel, Taylor's theorem about mu gives

    |integral g dnu - N g(mu)| <= (K/2) N Var(E)
      <= (K/2) N (b-mu)(mu-a).

The last inequality follows from (E-a)(b-E)>=0 and the fixed mean. Thus two positive spectra with the same moments differ by at most K N(b-mu)(mu-a). This is a derived conditional bound; an implementation must supply a valid K for the actual kernel. A numerical sample maximum is not a proof of a derivative bound.

Actual Verner cross sections cannot simply inherit the E^-3 inequality. Split panels at their actual species cutoffs and establish valid affine upper/lower envelopes or a derivative bound for each physical kernel. The resulting Gamma bound is multiplied by c n_H, not by the absorber abundance. Heat kernels require their own envelopes for epsilon(E-chi_i)sigma_i(E). A numerical high-precision comparison of selected kernels is a checked control, not a universal physical certificate.

## 6. Minimum independent acceptance matrix

1. **Source-free, opacity-free continuous export:** analytic density with nonzero support at the cutoff; arbitrary off-phase moving boundary positions; cumulative outflow continuous; out_E=epsilon E_c out_N; active count+out count constant; redshift work closes energy. At least one case exports the complete panel.
2. **Birth-to-export:** a photon cohort born inside a step and exported before the end. Its absorption, source, redshift, and outflow must use exactly one split characteristic history. A source-on lower-edge onset control must distinguish zero-trace onset from an artificial jump.
3. **Tail:** log f=-750 source-free continuation and source restart; physical positive tail-only export; positive weighted subnormal under normal total; deliberately wrong BE log update and scalar-zero deletion rejected.
4. **Moment restrictions:** exact binary64 endpoints and moment inputs; beta=0, beta=-width, both bracket ends, narrow supports, interior versus right-front restriction. Independent arbitrary-precision positive integrals, never the generating moments after f64 rounding, define the target.
5. **Coupled owner identity:** wrong f_He, stale gas stage, swapped cutoff/threshold, lost binding, or omitted work/escape/CMB must fail a real residual or independent budget assertion. Rejected trials cannot mutate accepted state.
6. **Projection:** same reconstructed input and prescribed path compared to higher-order positive quadrature; then repeated projections compared to history replay with identical event-local frozen rates/source. A continuum source integral is a separate reference and must not be mixed into the same-discretization comparison.
7. **Observable envelope:** endpoint-atom and mean-atom sharpness controls for E^-3; random positive interior measures contained in bounds; shrinking panels show decreasing gap; a moment-preserving spectral rearrangement changes Gamma while leaving both moments fixed.
8. **Temporal versus projection cadence:** hold projection epochs fixed when isolating time error. Projecting after every refinement substep changes the method and must be reported as mixed total-method error.

Record the original number/energy tolerances, reference-pair tightening, selected scientific fields, and all failed refinements. A small bounded test may establish a primitive or a finite experiment. It does not establish the long z=12 to 10 37-field certificate, full cosmological history, production integration, or anisotropic transport.

## Inspected files

- `research/transport_20261007/projected-radiation-bridge-theory/BRIDGE_DESIGN.md`
- `research/transport_20261007/projected-radiation-bridge-theory/TEST_FIRST_AND_RESOURCES.md`
- `research/transport_20261007/projected-radiation-bridge-theory/TAIL_DIAGNOSTIC.md`
- `research/transport_20261007/continuous-boundary-prototype-v2/FINAL_REPORT.md`
- `research/transport_20261007/continuous-boundary-prototype-v2/ARITHMETIC_ADMISSION.json`
- `research/transport_20261007/short-hhe-midpoint/FINAL_REPORT.md`
- `research/transport_20261007/short-hhe-midpoint/CONTRACT.json`
- `research/transport_20261007/short-hhe-midpoint/src/radiation.rs`

No candidate source was edited or candidate execution independently certified in this preimplementation review.
