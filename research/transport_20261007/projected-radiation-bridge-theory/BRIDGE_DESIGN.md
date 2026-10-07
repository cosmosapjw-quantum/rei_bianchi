# Projected positive-panel bridge: design only

2026-10-07 UTC. Design only; this note reports no implementation, solver history, or compilation. Midpoint acceptance was pending when the design was written; no later result is assumed. Existing V2, BE, midpoint, and baseline evidence is unchanged.

## 1. Recommendation and three gates

The minimal bridge replaces persistent characteristic samples by positive two-moment panels, while preserving the accepted gas residual/staging and shared characteristic owner kernel. Reconstruct and integrate the same continuous panel measure for stock, all absorptions, heat, redshift, and eventually the swept boundary. This is a numerical spectral approximation; it changes neither source nor microscopic physics.

Do not promise an unrestricted four-step success by simply connecting V2. V2 is a bounded normal-only pure-radiation PASS. The source-off low-energy wake can underflow already during the proposed four base intervals: the initial physical HI opacity is 1.3663e6 per unit ln(a). TAIL_DIAGNOSTIC.md gives the source-bound calculation and limitations. A projected panel may retain normal total moments while some physical quadrature contributions are tails; aggregate normality does not remove this issue.

Recommended sequential evidence gates:

1. Additive panel-integration and tail-arithmetic primitives, tested against independent controls; preserve V2 unchanged. Test actual source-created and source-off supports. If only normal-lane primitives are available, the honest outcome is a finite normal-fixture PASS plus a named four-step tail blocker.
2. Conditional on a reviewed midpoint acceptance and gate 1, a bounded coupled projected experiment over s0=-ln(13) through s0+8e-4, four base intervals of 2e-4. A base interval is a reporting/experiment unit, not a promise that one nonlinear transaction meets accuracy. Any temporal subdivisions must be declared, resource-admitted, and their projection cadence explicit.
3. Separate real-boundary experiment reaching beyond s0+ln(13.7/13.6), approximately s0+0.007326040092. The first four intervals have exact zero outflow for this initial/source fixture and cannot validate coupled outflow. No gate establishes z12→10, z6, p256, the 273-row/37-field certificate, production readiness, or runtime improvement.

## 2. Frozen scientific interfaces

Use s=ln(a), eta=s+ln(E/eV), f in photons/H/deta. E=exp(eta-s) eV. For each occupied support [L,R], retain

- N=integral f deta and M=integral exp(eta) f deta;
- U(s)=epsilon exp(-s) M;
- exact support provenance, ordinary versus source-front closure, physical empty/exported status, and authoritative tail representation.

Normal-lane N/M are still the physical raw moments. Do not replace them with fitted means or use reconstruction to repair an unrealizable pair. V2 DD normalization and its exact-binary64 input target 5e-13 remain applicable only within its declared normal domain: endpoints in [-32,32], exact width in [1e-7,32], and admitted beta in [-128,128]. That domain is not automatically enlarged by this design.

Photon owners remain A_i (absorbed photons/H), B_i (absorbed erg/H), Q_N/Q_E, redshift_E, out_N/out_E. Gas consumes precisely the same A/B:

- dxHII_photo=A_HI;
- dxHeII_photo=(A_HeI-A_HeII)/fHe; dxHeIII_photo=A_HeII/fHe;
- dw_photo=sum(B_i-epsilon CHI_i A_i).

The global material midpoint, affine endpoint gas path evaluated at each characteristic segment midpoint, actual segment background, zero-photo provider owners, nonlinear safeguards, CHI/CUTOFF distinction, source conversion, and exact-event anchor are inherited from the finally accepted midpoint contract. This document does not certify that pending implementation. Gamma must be an independent direct integral of c nH sigma_i f, even when the absorber fraction is zero.

## 3. Continuous supports and source fronts

For this zero-initial, always-on source fixture, the occupied eta range at s is [s0+ln(Emin), s+ln(Emax)], intersected with eta>=s+ln(Ec). A narrower actual panel support must be stored explicitly. The lower endpoint is initially fixed; the upper newly born source front advances. At s=s0 the spectrum is exactly empty, regardless of the nominal energy domain.

Every transaction splits integrations at existing panel/support boundaries and at s_start/end+ln(E) for E in {Emin,Emax,Ec,CUTOFF_HeI,CUTOFF_HeII}. Characteristic time integration further splits at exact source entry/exit and species cutoff times. Preserve exact binary64 topology; neighboring floats are not the same event. Current event anchoring remains mandatory, including rejection if exact start/end energy anchors are incompatible. No epsilon event bands, nextafter repairs, or energy replacement are introduced.

On a right source-front panel use V2's actual interior taper: with y=(eta-L)/(R-L), f proportional to (1-y) exp(beta y), not an ordinary exponential whose value is merely overwritten at eta=R. Its left-hand trace at R is zero, so moving support adds no fictitious source-front flux. An old right-front label cannot remain attached to an interior boundary merely because it once was the frontier. Splitting a front parent at C creates an ordinary left child and a right-front child after explicitly measured moment-preserving projection; an exact temporary restriction may instead retain the parent's taper until the next intended projection. Do not apply a new right-zero taper to the left child at C, where the parent is generally nonzero.

The initial lower support edge also has zero trace in the exact initially empty source solution: an eta=s0+ln(Emin)+u characteristic is supplied only for duration u before source exit, so f tends to zero as u→0. This is a fixed endpoint during the four-step proposal, hence no moving-face flux requires a zero trace there. The minimal V2-family bridge may use an ordinary closure there, but must disclose and test this lower-trace shape error. It must not claim exact source-onset shape. Before a real-boundary-onset claim, compare the lower-edge trace against the independent source-history reference; a left-taper family such as y exp(beta y) is a possible separate, explicitly tested extension, not already covered by V2. A whole panel crossing its neighbor cannot cure a wrong lower trace by bookkeeping.

Never merge across an empty gap, exported interval, or incompatible support provenance. At a geometry-empty intersection, zero is exact. A positive tail is not geometry-empty. Atomic data need an explicitly declared atom representation; no atom may be silently created when a narrow smooth cell is inconvenient.

## 4. Initial-moment-exact positive quadrature

Ordinary Gauss integration of the reconstructed density is not guaranteed to reproduce the authoritative stored N/M. Adding shared sink/source weights does not fix that mismatch. Use the existing proposed physical moment rule on each topology-split subinterval J=[a,b]:

n_J=integral_J f0 deta, m_J=integral_J exp(eta)f0 deta;
w_J=n_J>0, eta_J=ln(m_J/n_J).

This one-point rule is exact for 1 and exp(eta) under f0 deta in real arithmetic. It is constructed before owner evaluation; no weights are rescaled after a budget failure. Binary64 eta/exponential round trips remain measured errors, so the practical requirement is the original budgets and independent moment residuals, not a claim of bitwise exactness.

V2's analytic Density integration is not an integral implementation for every reconstructed Closure, especially its front taper. Required new closure-restriction formulas are explicit. Let W=R-L, y_a=(a-L)/W, y_b=(b-L)/W, and

Z_k(t;a,b)=integral_a^b (1-y)^k exp(t y) dy, k=0 ordinary or 1 right-front.

Then

n_J=N Z_k(beta;y_a,y_b)/Z_k(beta;0,1),
m_J=N exp(L) Z_k(beta+W;y_a,y_b)/Z_k(beta;0,1).

For k=0, an antiderivative is exp(t y)/t. For k=1 it is exp(t y)[(1-y)/t+1/t^2]. Direct subtraction near t=0 or nearby endpoints is forbidden: use positive scaled integrals, expm1/series, and tested t=0 and beta+W=0 limits. Log forms avoid lost amplitudes. The exact binary64 panel and subinterval endpoints, rather than nominal decimal widths, define the high-precision oracle. Sum of subinterval moments must match the incoming pair within separately reported arithmetic error; do not set the last child to an unexplained residual.

Evolve the initial-stock contribution with f=1,q=0 at eta_J, multiplying every returned owner and end moment by n_J. Evolve continuous-source contributions separately with f=0 using a positive geometric eta rule and the original q_s=Q_t/(C E H) on exact source-active segments. Add both positive transactions. Frozen linearity justifies superposition at a trial gas path; both components must be recomputed for each nonlinear gas trial.

The source component still uses the same segment-frozen q for its state, all Q owners, absorption, and redshift. Exact continuum source totals are independent consistency references only. Do not insert those totals as its ledger. Initial-stock weights with photon units and source geometric weights with eta units must not share an ambiguous API.

Endpoint energy convention must also be fixed: sum the returned active count N and the actual kernel-carried energy U using the same weights, then form the stored M=exp(s1) U/epsilon with checked shared-scale arithmetic. This defines the authoritative endpoint moment pair before reconstruction; retain preconversion U transiently for its round-trip/next-start audit, not as a third independent evolved moment. In exact arithmetic this equals integral exp(eta) f_end deta. Binary64 event anchors and the M↔U conversion can differ slightly from a direct exp(eta) count sum, so record that difference and enforce the inherited continuity and original budget gates. Do not select whichever energy convention makes the ledger close. For log/scaled tails use the same algebra without exponentiating the full amplitude.

Rebuild the moment-rule abscissae from current continuously cut subintervals each transaction. They are ephemeral integration devices, not persistent photon atoms. For later export, integrate the swept strip ending at tau(eta), instead of waiting for a stored quadrature stock to cross.

## 5. Endpoint projection, splits, and merges

At every declared projection epoch:

1. Integrate each physical transaction over the destination supports, recording positive endpoint N/M and every owner before fitting anything.
2. Complete the nonlinear gas root using the same integrated A/B. No reconstruction, split, merge, or finite-difference trial can mutate old state/ledgers.
3. Fit the admissible positive closure to the resulting N/M and actual support; verify the exact-input normalized mean and independently reintegrated moments. Projection changes only higher spectral structure, not moments or owners.
4. Perform deterministic, separately audited split/merge operations, then endpoint diagnostics on the committed representation. If a post-root representation fails, reject the complete candidate; do not keep its gas update or repair the radiation pair.

Topology and quadrature should be fixed for all residual/finite-difference evaluations of a Newton attempt. An adaptation that changes nodes at different endpoint perturbations adds a different, potentially nonsmooth residual map. If a predeclared error indicator requires refinement, discard the private attempt and restart from the same old state under a bounded explicit restart policy; this is an additional numerical policy, not an existing safeguard.

Splits integrate the parent closure on the child supports. They conserve both moments in real arithmetic but fitting separate children generally changes higher moments. Merges sum both authoritative moments using positive stable arithmetic and reconstruct over the connected union with the correct outer support metadata. They are not an exact inverse of the previous split. Roundoff, closure bias, and owner identities must therefore be tested separately.

Avoid obligatory closure fitting on arbitrarily tiny event-cut pieces: quadrature pieces are not automatically persistent panels. A final sliver narrower than V2's 1e-7 or with a mean outside beta±128 may be merged with an adjacent compatible occupied panel only as a declared moment-preserving operation, with its projection bias tested. It may not be rounded away. If no compatible merge exists or the merged target remains unsupported, reject with the exact geometry/mean blocker. Enlarging the bracket or narrowing width admission requires its own source and oracle evidence.

Source-off wakes can be very steep. At the initial lambda, the leading log-density gradient from varying source-exit age is O(1.37e6) per eta. A dark strip of width 8e-4 can thus involve a dimensionless tilt O(10^3), beyond V2's beta±128. This is a second likely coverage problem in addition to amplitude underflow. Finer subdivisions may help, but do not prove admission; record actual means, beta brackets, widths, and moments before deciding.

## 6. Authoritative tails: preserve the baseline contract, change the formula correctly

The accepted baseline distinguishes never populated/exported (-infinity log count) from positive stock with zero/subnormal readout (finite authoritative log count). Its source-free tail continues attenuating and its diagnostic photon L1 uses logs rather than discarding zero readouts. Identified numerical losses have dimensional N/E bounds, capped at 1e-20 photons/H and 1e-30 erg/H. These semantic contracts should be reused.

Do not copy the baseline BE update -log1p(lambda dt) into the exponential characteristic kernel. For the new segment, with h in s, correct authoritative stock is

log f1 = logaddexp(log f0-lambda h, log q+log J(lambda,h)),
J(lambda,h)=(1-exp(-lambda h))/lambda, with J(0,h)=h.

At q=0, log f1=log f0-lambda h even when f readout is zero. If lambda=0, a positive tail remains unchanged. Exact source-zero/empty semantics are separate; logs of zero-positive provenance cannot be regenerated from a rounded scalar. Carry endpoint energy/comoving moment logs from their physical characteristic relation and the same owners, not from a newly zero readout.

All positive stock/source/absorption/energy/redshift/outflow contributions require a checked scaled/log path before normal multiplication can lose them. A normal aggregate does not permit an unrecorded underflowing summand. Each species A_i and B_i shares the same stock/time measure. Compute owner formulas positively and stably; never derive missing absorption, heat, or redshift as a global budget residual. At physical export, move the authoritative surviving tail into the authoritative outflow owner before marking its active support empty.

For panels, two independently rounded large negative logs are insufficient for robust narrow-support closure: log M-log N can lose the small shape information even though amplitude survives. Minimal proposed additive tail state: a shared wide dyadic amplitude exponent plus normal scaled N/M mantissas, authoritative finite logs, support and closure metadata. The physical pair is N=2^k N_scaled, M=2^k M_scaled. This selects a shared-scale pair rather than leaving the implementation to subtract two large logs. The normalized-mean target remains 5e-13 for the exact supplied scaled mantissas and endpoints; separate log/amplitude and error-enclosure tests must be frozen before coding. Retain raw N/M as the normal-lane interface. Form the mean using the shared-scaled pair, never exponentiate both full tail logs and divide zeros. Admit and independently test consistency between mantissas, logs, support, and readouts. This is a new tail representation requiring review, not something implemented by V2's Inventory::LogTail tag. A convenient arbitrary floor or copying a mean from a neighboring panel is prohibited.

When converting a tail contribution to the unchanged normal-only material provider boundary, an explicit conservative dimensional error enclosure may accompany its zero/rounded readout, as in the baseline. The actual authoritative radiation stock and owner logs remain. Sum bounds at the point where the loss occurs, include weights and rate/time/energy units, and prevent double charging or missed scalar-zero paths. Common-scale summation can lose a tiny relative addend even when its physical magnitude is not below MIN_POSITIVE; bound that loss in the physical scale, never by an unscaled MIN_POSITIVE constant. Keep source/owner provenance sufficient to distinguish such scaled-summation loss from exact emptiness. Each provider-owned photo readout and radiation ledger uses the same rounded owner plus its bound. If a valid bound cannot be established, reject.

For new acceptance require abs(number residual)+underflow_N_bound <= original number allowance and abs(energy residual)+underflow_E_bound <= original energy allowance, in addition to the baseline cumulative bound caps. This is a conservative strengthening of the unchanged budgets, not an enlarged allowance. Allocate component/quadrature error separately; underflow bounds are not a place to hide reconstruction error. Gamma/L1 tail readouts likewise need bounds and retained log evidence.

Do not assert generic history readiness after this extension: scaled arithmetic, accumulated logarithm accuracy, narrow-cell realization, source restart, complete export, changing species masks, and stiff coupled admission each need their own tests. V2's existing fail-closed lane remains a valuable negative control.

## 7. Shared gas residual and budget audit

For an admitted trial endpoint y1, compute the same midpoint-theory residual R=y1-y0-P(A,B)-h G(y_mid,s_mid), with segment-centered affine gas used by radiation. The combined exact-real energy defect remains

R_w + epsilon[CHI_H R_HII + fHe CHI_HeI R_HeII + fHe(CHI_HeI+CHI_HeII) R_HeIII],

plus independently measured numerical moment/owner/roundoff error. Conservative N/M projection does not change this identity. It also does not establish time or spectral accuracy. Check budgets before and after representation changes; independently recompute endpoint U=epsilon exp(-s)sum M and binding from gas. Carry and compare preprojection physical energy, projected energy and next-start energy under the inherited 2e-12 continuity gate without replacing any value to match.

Every candidate accepted state retains the original number allowance 1e-10 max(emitted_N,1e-10) and full energy allowance 1e-10 max(emitted_E+work_E+escape_E+abs(cmb_reservoir_E),1e-20). Original 37 fields, field definitions, exact zeros and 0.1 retightening remain unchanged. Provider floors/caps and genuinely discontinuous diagnostics keep the midpoint theory's qualifications. No unconditional gas positivity, stiff accuracy, or all-field order-two assertion follows.

## 8. Projection bias and independent references

Use four logically distinct comparisons:

A. Same reconstructed input and prescribed gas path: candidate moment-rule stock quadrature versus independent positive higher-order continuous-density integration. This measures owner quadrature error, not accumulated projection bias.
B. Same prescribed gas path and numerical source/rate history: project after each declared epoch versus replay all characteristic segments without projection. Replay must use exactly the same event-local frozen q_s and lambda approximations, gas path, anchors and time partitions as the projected lane. Replacing them with continuously varying q_s or a different rate quadrature would mix time/source consistency error into this comparison. Replay stores a bounded list of past accepted gas-path descriptors and evaluates f(eta) from that history at fresh integration points; it does not interpolate old nodal values. This isolates projection accumulation plus a separately bounded quadrature difference. Its outer eta integration must split at the transformed source/threshold/staging edges from all retained past gas-path descriptors, or use an independently certified adaptive alternative. Count those actual historical integration intervals C_ref and oracle nodes separately; the current-transaction C<=P+10 estimate does not apply to replay.
C. Fully coupled projected versus self-consistent unprojected replay at the same temporal partitions. This includes projection feedback into gas. A fixed-node reference on the matching interval can supplement it, but is not a continuum boundary oracle, especially after export.
D. Independently tighter continuous-time physical reference, only within a separately specified resource envelope and with both reference members admitted. The existing s0→s0+2e-4 reference is not a four-interval endpoint oracle. No extrapolation or incomplete long reference is accepted as truth.

Measure local projection defects in all three Gamma kernels, absorption/energy/heating functionals, and photon-number/energy L1 as well as both conserved moments. A two-moment-preserving reconstruction can alter an E^-3 observable and future gas evolution. V2's isolated source E^-3 bias control is evidence for its fixture only. Use shared positive-domain quadrature to integrate absolute reconstructed-density differences; log-difference methods must include tails. Partition the error report into temporal, owner quadrature, projection, reference tightening, and floating/tail components.

Refining time while projecting at every smaller step changes projection frequency. Such a run is a legitimate total-method convergence experiment but not a pure temporal study. To isolate time error, hold the projection epochs fixed (e.g. the four base boundaries), perform unprojected substeps inside each base interval, and project only at the fixed epochs. To assess the operational every-accepted-step projection, run that separately and name the mixed error honestly. Output-only interpolation/reconstruction cannot change the primary trajectory. Off-phase observations must be read-only private evaluations; a rerun with a different output schedule should reproduce the same primary path.

## 9. Later real boundary, not part of this four-step proposal

For s beyond first source-export onset integrate the full physical swept strip [b(s0),b(s1)] intersected with occupied support:

Delta out_N=integral f(eta,tau(eta)-) deta,
Delta out_E=epsilon Ec Delta out_N, tau=eta-ln(Ec).

Include within-step birth, absorption, redshift and export using the same characteristic history and positive weights. Persistent panels integrate continuously shrinking support; ephemeral quadrature points never own an indivisible exit stock. Test arbitrary off-phase boundary positions, passage through old quadrature locations, lower-edge source onset, tail-only export, and complete panel removal. Smooth density gives continuous cumulative outflow; genuine atoms can have physical jumps. Four steps with out_N=out_E=0 cannot pass any of those nonzero-export claims.

See TEST_FIRST_AND_RESOURCES.md for the bounded evidence ladder and explicit accounting to freeze before coding.
