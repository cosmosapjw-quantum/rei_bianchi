# SHARED_C64_R3: lifted homotopy gate, rho domain, total-error firewall, and a-priori pruning

Date: 2026-09-28. Scope: research only. No production source, Eq.(55) probability, scientific tolerance, Nmax/channel authority, or continuum-ionization authority is changed.

## Fresh state used for R3

Immediately before R3 publication, PR #17 was fresh-read at head 96a6e4317a54e9eae825f66292743f9785df80e0. Relative to the prepared execution commit aac8f822dc10a215e7c59259bd339965c4ffe23c, that head was exactly one evidence-only commit ahead. PR #15 remained at af3ed44ce3cc1023aa8a1370ab2981aa76760869 and PR #16 remained at 2c3812e390b91b89da1de30988b3933646b79f30.

The R2 follow-up executed immutable commit aac8f822dc10a215e7c59259bd339965c4ffe23c, tree 765a8d3133bc30eea6bc6e00e50424cc288fd56c, using only the stdlib verify-only path. Seven trace inputs matched their exact size/SHA contract. The host lacked pytest, NumPy, and SymPy, so no saved-trace numerical replay or scientific suite was run there. This is INPUT_IDENTITY_VERIFIED, not scientific validation.

## 1. Lifted-homotopy claim gate

Let Sigma be the spectral Riemann surface carrying the selected two sheets, with projection pi to the complex R plane. For fixed rho define the action one-form

    omega_rho = G(tilde R) K(rho, pi(tilde R)) dR,

where K(rho,R) = (1-rho^2/R^2)^(-1/2).

If the original lifted contour and a proposed common lifted contour are fixed-endpoint homotopic on Sigma through a region free of singularities of omega_rho, their action integrals are equal. If their base contours differ only by a real-axis bridge whose integrand is real, their imaginary actions are equal.

Therefore the unresolved common-contour authority is topological. A small sampled sheet gap, small spectral residual, or 32/64 agreement does not prove the required lifted homotopy.

For the finite-CF spectral system F(z,R)=0 with z=(p,lambda), regular sheets are locally analytic where det(dF/dz) is nonzero. A future global certificate must exclude unintended solutions of

    F1 = 0,
    F2 = 0,
    det(dF/dz) = 0

throughout the swept homotopy domain except the intended certified fold, while also excluding continued-fraction chart poles and kernel singularities and preserving the intended monodromy/winding class. Interval/Krawczyk or argument-principle exclusion over a cell decomposition is the natural authority candidate.

Status: DERIVED CLAIM GATE. Global certificate remains OPEN. Common-contour replacement remains RESEARCH_CANDIDATE_NOT_PRODUCTION.

## 2. Exact analytic disk in rho

For fixed nonzero R, K as a function of complex rho has branch points at rho = +/- R. For a compact contour Gamma define

    r_star = inf over Gamma of |R|.

The Taylor/binomial germ about rho=0 is analytic for |rho| < r_star, and r_star is the exact radius of the common Taylor germ because the nearest kernel singularities are the set {+/-R : R in Gamma}.

This does not imply that r_star is the maximal interval along positive real rho. If the nearest singularity is off the real axis, real-axis continuation can in principle extend farther. Hence production logic must distinguish the certified open disk from the still-open maximal real-rho interval.

The R3 helper computes only the finite-trace analogue min_j |R_j| and labels it FINITE_TRACE_KERNEL_ONLY.

Status: DERIVED. Finite-trace implementation checked. Maximal positive-real rho interval OPEN.

## 3. Total-error firewall

Only after the same-sheet lifted homotopy is separately certified may numerical error components be composed as

    E_total <= E_spectral + E_quadrature + E_rho_interp + E_roundoff.

Homotopy is a logical gate, not a guessed small epsilon. The R3 error composer fails closed when homotopy_certified is false.

If an actual pointwise spectral enclosure |Ghat-G| <= eps_G is available on the same contour and q=(rho_max/r_star)^2 < 1, then

    E_spectral <= (1-q)^(-1/2) integral eps_G |dR|.

The existing 32/64 shared-node gap is not an exact-spectrum error enclosure, and 32/64 Simpson agreement is not by itself a rigorous quadrature remainder. Floating-point production certification still needs interval/ball arithmetic or a forward-error enclosure for kernel evaluation and summation.

Status: STRUCTURE DERIVED. Numerical total bound BLOCKED by homotopy, spectral, quadrature, and roundoff authorities.

## 4. A-priori hybrid pruning bound

R2's exact telescope depended on the true downstream adjoint, so it did not authorize pruning before exact event probabilities were known. R3 adds the following conditional theorem.

Assume cheap approximate probabilities q_e and certified radii

    |p_e - q_e| <= eps_e

are available without performing the exact expensive event calculation. Let Q_e and T_e have the same supported reversible or one-way sink topology, let y_e^Q be the approximate upstream state, and let lambda_e^Q be the downstream adjoint computed only from Q. For a bounded observable w define

    osc(w) = max(w) - min(w).

Column-stochastic events do not increase oscillation. A downstream telescoping bound gives

    ||lambda_e^T - lambda_e^Q||_inf
        <= osc(w) sum_{k>e} eps_k.

Hence the true two-state downstream sensitivity obeys

    |lambda^T_{e,j} - lambda^T_{e,i}|
        <= S_e,

with

    S_e = min(
        osc(w),
        |lambda^Q_{e,j} - lambda^Q_{e,i}|
        + 2 osc(w) sum_{k>e} eps_k
    ).

The exact hybrid contribution therefore satisfies, without knowing p_e,

    reversible: |c_e| <= eps_e S_e |y^Q_{e,i} - y^Q_{e,j}|,
    sink:       |c_e| <= eps_e S_e y^Q_{e,i}.

Summing these per-event bounds gives an a-priori observable-error certificate. It becomes an operational pruning rule only if q_e and eps_e are genuinely cheaper to obtain than the exact event probability. If eps_e itself requires exact Eq.(55), there is no pruning advantage and no authorization.

The constant-observable limit is exact: osc(w)=0 gives zero observable-error bound.

Status: DERIVED, conditional on valid cheap event-error contracts.

## 5. Implementation and validation

Research-only files were added under research/shared_c64/20260928/R3. The production package was not modified.

TDD record:
- RED: the focused test module was written before implementation and failed at collection with ModuleNotFoundError for common_contour_contract, exit 2.
- GREEN: 6 focused tests passed after the minimal implementation.
- full repository suite: NOT RERUN.
- spectral solves: 0.
- cloud runs: 0.

Synthetic validation used 10,000 random chains with 5 states and 14 events, sampling true p within the promised q +/- eps balls:
- violations: 0;
- max actual / pruning bound: 0.6679238167834242;
- median actual / pruning bound: 0.1276269370683498;
- median pruning bound / sum eps: 0.031717352670177036;
- p95 pruning bound / sum eps: 0.05999488449600928.

These numbers are SYNTHETIC STOCHASTIC VALIDATION ONLY. No atomic probability, Eq.(55), cross section, or production speedup is claimed.

## 6. CODE-I02 independent rereview preparation

The independent decision must target PR #15 at exact head af3ed44ce3cc1023aa8a1370ab2981aa76760869. PR #16 resume-004 is supporting runtime evidence only.

The reviewer should explicitly inspect endpoint binding of state_a, state_b, R, p, lambda, depth, Z1, Z2, membership tolerance, probe scale, and policy identity; verify that validation occurs before geometry; add or independently exercise stale attacks for state_a, tolerance, probe_scale, malformed/missing hash, and malformed permutation; distinguish stale-copy binding from certificate authenticity; and check whether non-revalidated diagnostic fields are consumed downstream.

The SHA256 binding is unkeyed self-consistency, not provenance authentication. A jointly fabricated endpoint plus certificate plus recomputed hash is outside the stale-copy guarantee unless the claim is explicitly strengthened.

A separate self-contained reviewer handoff is published as CODE_I02_INDEPENDENT_REREVIEW_HANDOFF_KO.md. This authoring thread does not self-certify independence.

## Gate after R3

- CODE-I01: CLOSED.
- CODE-I02 implementation and cloud runtime: PASS evidence exists.
- CODE-I02 focused independent scientific rereview: REQUIRED / NOT RUN here.
- common-contour lifted same-sheet homotopy: OPEN.
- kernel rho Taylor disk: DERIVED; finite-trace implementation CHECKED.
- maximal positive-real rho interval: OPEN.
- total numerical error: STRUCTURE DERIVED; values BLOCKED.
- hybrid pre-computation pruning: DERIVED + SYNTHETICALLY_CHECKED, conditional on cheap certified event-error radii.
- scientific_PROMOTE = HOLD.
- Eq55 = NOT_RUN.
- continuum_ionization = NOT_ADMITTED.
