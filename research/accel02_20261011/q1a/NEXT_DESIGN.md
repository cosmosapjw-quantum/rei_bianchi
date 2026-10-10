# Bounded next design after fixed-point source quadrature remains inadequate

Status: **proposed Q1B numerical representation; no implementation, ODE, new source-reference calculation or test execution in this note**. Model identity UNKNOWN. This note consumes the completed source attribution and the root's new Q1A preflight report: G1 and G2 source-number errors against the saved reference are approximately 0.06835466003 and 0.03448234347, giving a prospective pair lower bound around 0.03274, already above the unchanged 0.001 spectral target. The new whole-interval G1/G2 and G1 time-refinement trajectories are separate, currently executing evidence; their outcome is not inferred here.

Recommendation: complete and preserve the bounded Q1A trial, then select **fixed q cells with independently evolved number and energy moments**, analytically integrated HM12 cell source moments, and threshold-split native-opacity integrals. Do not start another point-grid escalation. Exact source integration alone cannot certify evolved opacity/heat moments, so use cheap local go/no-go gates before another coupled ODE.

## 1. What changes, and what stays the same

Current Q1A transports weighted point packets with one fixed q and one initial direction per packet. Replacing S(q_i)w_i by an exact cell-number integral changes this semidiscrete operator: the resulting energy source q_i S_0 generally differs from the exact cell energy source S_1. Assigning that discrepancy only to a counter would break photon/gas/energy pairing. Likewise, improving displayed Gamma or heat without changing photon depletion is inadmissible.

Q1B instead defines the state as integrals over fixed covector cells. This is an explicit **numerical reconstruction/closure change**, not an unchanged point-packet scheme and not new physical emissivity. The pinned HM12 interpolation, native cross sections, H/He gas/Case-A physics, geometry, conditional IC, physical source band and all scientific tolerances remain unchanged. There is no source smoothing, provider replacement, CR/RCT introduction or change of chemical energies to match rounded cross-section cutoffs.

The fixed covectors remain q and mu_0. Inside each angular ordinate, E=R(t,mu_0)q, with R independent of q and dR/dt=-lambda R, lambda=H+s(3mu(t)^2-1). Integration points inside a cell may depend on the current threshold and reconstruction: they are temporary quadrature points, **not transported state nodes**. State-cell boundaries and angular weights do not move.

## 2. Conservative two-moment equations

Let F_c(q,t) be the reference-volume photon density per d ln q, including the fixed normalized angular weight, within the fixed cell [q_L,q_R]. Define

    N_c = integral F_c d ln q,
    Q_c = integral q F_c d ln q,
    U_c = R Q_c.

N has units reference cm^-3, Q has units eV reference cm^-3, and U is photon energy in eV reference cm^-3. **Store N and U**, with Q=U/R reconstructed at the current time. This makes both the photon-number sum and the photon contribution to the total energy linear in the stored state, instead of recovering number through a time-dependent point-energy denominator. It does not remove the physical expansion work.

For absorber a, define integrals without dividing by the absorber density:

    K_0,a,c = c integral sigma_a(Rq) F_c(q) d ln q,
    K_1,a,c = c integral q sigma_a(Rq) F_c(q) d ln q.

With current proper absorber density n_a, the equations are

    Ndot_c = S_0,c - sum_a n_a K_0,a,c,
    Udot_c = R S_1,c - sum_a n_a R K_1,a,c - lambda U_c.

For the existing reference volume V=a_rel^3, use exactly the same integrals in the native gas calculation:

    Gamma_a = sum_c K_0,a,c / V,
    photoheat_per_absorber_a
      = eV_to_erg sum_c (R K_1,a,c - chi_a K_0,a,c) / V.

These formulas remain defined when n_a=0; never calculate Gamma by dividing an absorption count by n_a. The chemical gain is chi_a n_a K_0,a,c and the excess heat is n_a(R K_1,a,c-chi_a K_0,a,c), whose sum is n_a R K_1,a,c. Thus the photon loss, species production and energy transfer close by construction using one set of integrals. Retain the native chemical chi_a and the distinct native sigma thresholds as inspected constants.

The counters receive sum_c S_0,c, sum_c n_a K_0,a,c and eV_to_erg sum_c R S_1,c from this very same operator. Radiation expansion work is eV_to_erg sum_c lambda U_c. Existing thermal expansion, Case-A escape, signed CMB exchange and gas/nuclear bookkeeping remain at their current call sites. The angle-dependent photon pressure moment uses the same U_c and physical direction, which is q independent along the chosen initial direction.

This algebra is a **derived conservation identity**. Floating implementation, thermal/stiff evolution and global ledger performance still require verification. The existing initial-energy and initial-nH normalizations must remain unchanged in meaning; a source-budget normalization cannot replace them.

Independent proposal review (`review/Q1B_PROPOSAL_REVIEW.json`) confirms the algebra, with no implementation or ODE admission. Here V is the dimensionless proper/reference volume ratio. The absorption counter sums over both species and cells. In every angle sum, R_c and lambda_c remain inside the sum. For anisotropic geometry, a finite angular quadrature sum of w_mu R^-3 is not automatically a_rel^3: its angular integration error must be assessed separately. Reusing the FLRW source references does not certify a nonzero-shear calculation.

## 3. Exact cell source integration is the cheap part

At a given time, source support within a cell is the physical-energy intersection

    E_lo = max(R q_L, 10 eV),
    E_hi = min(R q_R, 50000 eV).

If E_hi<=E_lo, both source moments are exactly zero. Otherwise, using the fixed angular weight w_mu and the same HM12 proper source s_log,

    S_0,c = w_mu R^-3 integral[E_lo,E_hi] s_log(E,z) d ln E,
    S_1,c = w_mu R^-4 integral[E_lo,E_hi] E s_log(E,z) d ln E.

The existing source-pinned HM12Table.moment with powers 0 and 1 supplies these integrals exactly for its declared piecewise-linear-in-logE ordinate interpolation, up to floating arithmetic. Duplicate native jumps contribute zero measure and remain distinct one-sided values in the source provider. Exact source moments do not mean the physical HM12 continuum or its extrapolation is exact.

Use the same construction for initial UVB N_c and Q_c at R=1, with UVB as initial field only. Exact cell IC moments do not recover the full subcell initial spectrum; that information loss belongs to the reconstruction error budget. Cells straddling initial UVB jumps should therefore be split at those jumps.

Summing S_0,c and R S_1,c over cells must reproduce the already accepted source references at the saved 129 epochs and original 65 subset. This is a **new-cell-implementation check against saved evidence**, not a rerun of old Q0. It should be performed before ODE execution. Closed-form cell moments eliminate the moving-source-band point-quadrature error itself; they do not eliminate moving-opacity or subcell-spectrum error.

## 4. Opacity/threshold integration and reconstruction

Within each fixed cell, split temporary integration intervals at the three current atomic thresholds divided by R and at support boundaries. Evaluate the unchanged native sigma provider on these intervals. Use one positive converged quadrature to form K_0 and K_1 simultaneously; obtain heat by their paired combination, or by the algebraically equivalent common integrand when cancellation requires it. Do not use an E^-3 stand-in for production cross sections merely because a helper integrates that power.

A concrete first reconstruction to prototype is a normalized positive power law on active support,

    F_c(q) = N_c (q/q_*)^p / Z_0(p),
    Z_k(p) = integral_active q^k (q/q_*)^p d ln q,
    Q_c/N_c = Z_1(p)/Z_0(p).

The arbitrary fixed q_* only improves numerical conditioning. The mean q is strictly increasing in p for a nonzero interval, since its derivative is Cov(q,ln(q/q_*))>0. Hence every strict interior mean has one p. Evaluate the Z functions with stable log/expm1 forms and explicit limits at p=0 and p=-1. Endpoint-concentrated limits must be handled explicitly; do not fabricate a large finite p and call it exact.

This reconstruction is **a proposed numerical closure**, not an exact evolved spectrum. Threshold splitting removes quadrature aliasing of a jump for a given reconstruction, while finite-cell reconstruction error remains. Compare a predetermined cell pair and a separate temporary-integration-order pair; do not confuse these two error sources.

Realizability requires N>=0 and q_L N<=Q<=q_active,max N, with U=RQ, and N=0 implies Q=U=0. Retain photons below 10 eV after emission; 10 eV is a source cutoff, not an absorption/deletion boundary. For the expanding-axis geometry the upper active support is min(q_R,50000/R), since cells above the entry front must remain empty. Reconstruction may not put photons into the still-dormant E>50-keV region. Integrals remain over fixed cells; support restriction is part of the subcell representation, not a new advection/remapping term.

At an interior state, derivatives of opacity moments can be formed from the same quadrature. For B_k=mean[q^k kappa(q)] and m=Q/N,

    d(N B_k)/dQ = Cov(q^k kappa,ln(q/q_*)) / Cov(q,ln(q/q_*)),
    d(N B_k)/dN = B_k - m d(N B_k)/dQ.

Transform these to N,U variables with Q=U/R at fixed time. This supplies the new within-cell moment coupling absent from the current diagonal photon Jacobian. Gas derivatives still include the current absorber densities and native gas response. **The old point-packet photon Jacobian is not reusable unchanged.**

The empty-cell origin is a genuine implementation risk: a homogeneous reconstruction depending on Q/N is generally not differentiable there in all directions. An arbitrary finite-difference column can leave the realizability cone even at an otherwise valid state. Specify an admissible source-entry/empty-cell treatment and an appropriate directional/generalized Jacobian or verified start procedure before ODE execution. A zero-cell NaN hidden behind clipping or an undocumented mean-q floor fails the local gate. The continuous moment equations have inward source directions at the cone boundaries; a generic BDF step need not preserve that cone, so accepted-state checks and documented stage handling are still required.

## 5. Native integration boundary

Prefer an explicit versioned native integrated-photo-input path that accepts or computes the common K_0/K_1 and exact source moments, then calls the **same** igm_point_rhs and axisym_coupled_derivative. Preserve those native source-ledger and state guards. The cell integrator owns N/U, while the native gas receives the paired Gamma and heat; no second gas microphysics implementation is needed.

An adapter that reuses the existing packet ABI is possible only if temporary photon/source quadrature reproduces both stored N/U and exact S_0/S_1 with positive weights and consistent aggregation. Ordinary sampled reconstruction weights are not automatically moment exact, and assigning an exact cell source to one pre-existing packet is not adequate. Such an adapter must demonstrate its own moment matching and common-operator identities before it is accepted. The integrated-photo-input route makes these obligations more explicit and avoids presenting scratch nodes as independently transported photons.

## 6. Prospective bounded spatial choice

Prototype one cell family before any ODE: start with 64 uniform log-q base cells on 10..q_max, union the initial UVB duplicate-energy jumps, exact physical thresholds and 50000-eV initial support edge. Native source jump 54.37903440052643 eV must remain distinct from the 54.42-eV cross-section threshold. This gives roughly 90 cells, depending on exact deduplication. Use the same two angular ordinates initially. Freeze the enriched member by bisecting each cell in log q once, preserving every old edge.

This allocation is a prospective cost-bounded example, not a claim that about 90/180 cells suffice. Calculate the exact count and freeze its manifest when implementing. Exact source moments do not require source-table knots to be state-cell boundaries. Initial opacity/heat and reconstructed native-spectrum checks below may reject this family **without any coupled ODE**. If rejected, make one explicit feature-informed redesign with a fixed budget, or document that this chosen reconstruction is inadequate; do not silently grow the grid until a plot looks smooth.

## 7. Cheap go/no-go DAG before another ODE

1. **Q1B0_CONTRACT_AND_INVARIANTS.** Freeze state variables, units, reference volume, fixed cells, angular weights, reconstruction, active support, exact source moments, native ABI and counters. Independently inspect the number and energy identities above. Any undefined empty-cell/endpoint treatment or missing Jacobian term is NO-GO.
2. **Q1B1_SOURCE_IC_MOMENTS.** Sum the new cell source and IC moments and compare to the saved accepted full-band and threshold-selected references. Include off-grid entry positions, exact boundary coincidence and empty intersections. Retain both N and energy comparisons. Suggested *additional engineering* target: scaled differences <=1e-12 against the fixed saved reference amplitudes, with exact zero when the reference amplitude is zero. This stricter local check does not change any global criterion. Failure is an implementation/support error; do not run a coupled ODE.
3. **Q1B2_RECONSTRUCTION_AND_OPACITY.** Test positive power-law normalization/moments on interior, near-boundary, empty and partially entered cells. Use independent analytic constant-opacity and polynomial-opacity manufactured cases, including a moving step inside a cell, to check K_0/K_1 and common heat/chemical pairing. Manufactured opacities remain test fixtures only. For the actual native sigma, compare two predetermined temporary quadrature orders on the same reconstruction and independently evaluate initial UVB-weighted Gamma/heat at native discontinuity splits. This separates numerical integration error from reconstruction error before evolution. A useful local headroom target is 1e-4 for nonzero reference-amplitude normalized moment differences; it is not a new global tolerance or a continuum certificate.
4. **Q1B3_NATIVE_AND_JACOBIAN.** Verify the integrated-photo adapter against unchanged native gas behavior for matched inputs, its local number/energy cancellation, nonnegative species photo-rates/excess heat, and the new coupled N/U Jacobian against independent admissible-direction differences. Include n_a=0, exactly empty support and source entry. Check cancellation at the native local guard's existing budget; do not redefine that guard. An invalid-stage failure may be a solver-interface/closure issue, not physical negativity. Classify it accurately and stop before a full run.
5. **Q1B4_BOUNDED_EXACT_EVOLUTION.** New cheap manufactured checks only: source-only N/Q integral addition, expansion-only N constant and U/R constant, and constant-grey-opacity attenuation where the chosen reconstruction family remains invariant. These have analytic moment solutions and exercise work/counter signs and zero-cell activation. Do not use arbitrary energy-dependent opacity as an allegedly exact closure-preserving test. This node is a new capability gate, not an old RUN002/EVENT003 replay.
6. **Q2B_FULL_INTERVAL.** Only after all local gates close, run the frozen candidate/enriched pair on the complete z=15.9→4 interval and establish same-grid temporal evidence for the new representation. Check the unchanged 2e-6 temporal fields, 1e-9 initial-energy and initial-nH ledgers, 1e-11 geometry, strict domains/positivity and 1e-3 spectral target. Report nine history fields plus source/radiation-energy/species-heat moments for 129 and 65 epochs separately. Store raw outputs durably immediately at completion or first failure.
7. **Q3B_DECISION.** An independent reviewer classifies physics, reconstruction, quadrature, solver and implementation errors separately. Only an admitted new history can unlock the next Bianchi pair and subsequent actual BASS native receiver binding. Existing reduced N4 adoption remains scoped evidence.

The new cheap checks may be parallelized after the contract is frozen: source/IC intake, independent opacity integrals, and Jacobian/adapter review have distinct owners. No later ODE should begin merely because file schemas or a few conservation fixtures pass. Conversely, once these bounded checks close, proceed to the whole interval rather than starting an open-ended audit loop.

Every local gate gets an immutable decision/evidence manifest. Each completed run or first failure gets a raw checkpoint before report generation. Preserve the present Q1A results even if the analytic-source candidate later succeeds; neither exact source integration nor a local manufactured PASS retroactively changes the Q1A scientific decision.
