# Unit8 Li: finish independent ready outputs after BDF HOLD

Frozen 2026-10-17. This is completion of original dependency-safe work and
missing verification, not a second BDF repair. The root controller authorized
this continuation after the single balanced-BDF attempt failed. No BDF retry,
alternate independent solver or tolerance change is authorized.

## Evidence classification and admission boundary

Original and balanced BDF both stopped at u=0.5673291649750605 with the same
208 RHS evaluations, 8 Jacobians and 74 LU decompositions. The dyadic wrapper
check passed exactly; balancing did not resolve the observed precision stall.
The one repair is consumed. Preserve all original and continuation failures.

The saved ground Radau output remains a completed production solve whose
independent-solver validation is HOLD. Rate tables, the pending Radau rate-grid
and Be-source-grid comparisons, total-RR sensitivity, stationary diagnostics
and ledger reconstruction do not depend on BDF success. Complete them within
the remaining budget. A failed dependency blocks only claims requiring it.

The aggregate full kinetic admission must remain
`PARTIAL_READY_BDF_REFERENCE_HOLD` even if all other checks pass. Preserve an
explicit failed/missing BDF gate in tests, summary and execution evidence.
Never convert absence of BDF comparison into a passing comparison or call the
trajectory independently solver-validated. A passed rate block may be admitted
separately; successful Radau histories and sensitivity are provisional model
outputs. Ledger PASS means internal mass/charge/electron consistency only.

## Frozen scaled energy check and preserved raw diagnostic

The previously aggregated unscaled W=K+Q residual 3.6705962846958525e-7 is
localized to HI at T=223.872113856834K: W=1.346009e-317,
K=1.9046e-320, Q=1.344104e-317 J/s. These values are subnormal binary64
numbers. The original theory already requires scaled/log checks when physical
values underflow. This is application of that existing rule, not tolerance
relaxation or rate alteration.

Reconstruct from saved raw rows the scaled identity

    scaled_photon[2] = scaled_photon[3] + x0*scaled_photon[1].

Apply the original 2e-8 relative limit to every photon row with Tg>0. Also apply
2e-8 to raw W=K+Q on rows where max(W,K+Q) is at least
numpy.finfo(float).tiny. Keep the original all-row raw maximum, worst row,
subnormal classification and exclusion count as diagnostics. No loose SI
absolute floor, output clipping, numerical rate change or subnormal zeroing.
Any normal-range failure remains a failed energy check; do not repair it here.
The existing same-T beta/alpha identity uses shared quadrature and must be
labeled algebraic consistency, not independent numerical verification.

## Complete the missing independent detailed-balance spot check

The root authorized exactly 18 spots: the six frozen ground channels at
T=300,1e4,1e6 K. This does not repeat rate-table quadrature. Use two independently
implemented callbacks and separate scipy.integrate.quad calls, in different
physical coordinates. Let chi be threshold in joules, x0=chi/(kB*T), and
sigma_Mb the unchanged provider cross section in megabarns.

Photon-energy coordinate x=epsilon/(kB*T):

    Ibeta = integral_[x0,x0+80] sigma_Mb(kB*T*x)
            * x^2 * exp[-(x-x0)] / [-expm1(-x)] dx.

Electron kinetic-energy coordinate y=(epsilon-chi)/chi:

    Ialpha = integral_[0,80/x0] sigma_Mb(chi*(1+y))
             * (1+y)^2 * exp[-x0*y]
             / [-expm1(-x0*(1+y))] dy.

Convert energies passed to provider.sigma to eV explicitly. Retain the original
finite window and t boundaries 0,1,4,16,40,60,80, with the LiI branch inserted
when applicable, mapping each boundary to x=x0+t or y=t/x0. Use epsabs=0,
epsrel=2e-12, limit=100 for these positive integrals. Do not reuse either
computed integral or set one rate from the other.

With C=8*pi/(h^3*c^2) and D=d*(2*pi*me*kB*T/h^2)^(3/2), form

    log_beta = log(C) + 3log(kB*T) - x0 + log(Ibeta) + log(1e-22),
    log_alpha_cm3 = log(C) + 3log(chi) - log(D)
                   + log(Ialpha) + log(1e-22) + log(1e6),
    log_S_cm3 = log(D) - x0 - log(1e6).

Require |expm1(log_beta-log_alpha_cm3-log_S_cm3)| <=2e-8, the original frozen
identity limit. Crosscheck Ibeta*1e-22 and x0^3*Ialpha*1e-22 against the beta
and stimulated-alpha scaled values, respectively, in the matching saved
independent_quad_checks.json row, using the original independent_quad 2e-8
relative limit. Export all 18 integrals/log values/residuals and QUADPACK error
estimates. Failure limits the rate admission; no adaptive follow-up is allowed.

## Remaining original work

Add `code/li_thermal_finish_ready.py` rather than replacing the failed repair
runner. Load unchanged saved rate tables, production and inputs. Reconstruct
all existing checks from preserved evidence. Run each of the originally
pending ground257, ground_half_Be and total_RR_sensitivity Radau solves once,
using the original RHS/Jacobian, initial state, rtol=1e-8, atol=1e-13 and grids.
Compare the first two against saved production at the original 1025 points
with the original 5e-6 absolute per-origin limit. The total-RR difference is
model sensitivity, with no requirement to be small.

Serialize success/message/partial result for each block before evaluating its
acceptance. If a block fails, mark only dependent outputs unavailable and
continue other independent originally authorized blocks while budget remains.
Do not retry a failed block. Preserve successful outputs already produced.

Finish the originally specified charge histories, selected-z diagnostics,
stationary/Saha comparison, availability map, inventory17 and full residual
ledger for available trajectories. Saved production selected-z diagnostics
use the previous amendment's explicitly labeled PCHIP reconstruction; history
and ledger use actual saved output-grid populations. Preserve all original
normalization, positivity, ledger and tiny-fraction limitations. Neither a
stationary distribution nor a new BDF approximation may replace dynamics.

Return scoped check groups for rates, ground production invariants, two Radau
resolution comparisons, total-RR invariants/sensitivity, ledger and BDF. Retain
the original full-suite failed solver gate, with overall PASS false. Separate
`completed` from `passed` and from `admitted`; publish a clearly bounded partial
result rather than deleting failed criteria or abandoning completed work.

## Remaining cumulative budget and executable transition

Original actual elapsed remains UNKNOWN. Accounting consumed is
3 + 0.460839424 + 0.695808747 = 4.156648171 seconds. Remaining allowance is
25.843351829 seconds. Use one thread and exactly one new process with timeout
25s and internal deadline at most25s, including all new checks and validation.
Measure command wall time and add it to prior cumulative accounting. No table
or production rerun, BDF call, second repair, solver ladder or numerical retry.

Independent repair-review PASS authorizes immediate coding and one execution
of this continuation. On completion or deadline preserve the scoped outputs
and hand them to independent review. No further process-only prerequisite is
introduced; missing BDF validation continues to limit claim admission.
