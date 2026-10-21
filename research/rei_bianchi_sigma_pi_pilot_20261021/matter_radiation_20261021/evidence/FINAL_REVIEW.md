# Independent component-result review — PASS_SCOPED_PRELIMINARY

Reviewer: `/root/pilot_independent_review`, independent and nonimplementing. Requested Astra role; developer context identifies GPT-6 Astra Pro, without additional runtime model telemetry. The reviewer wrote only review/audit artifacts, implemented no solver and ran **no ODE trajectories**.

**The component extension passes for scoped preliminary publication. No blocking findings or required repairs remain.** Production admission remains NOT_ISSUED. The original completed625 pilot remains preserved.

## Source and physical interpretation

Reviewed `component_pilot.py` at SHA `e2ce8b440765be3a728d8127a4f1085dbc304cabcaa7a5d4e892f92ccabd801e`, component plots/tests, NCP wrapper, frozen contract, theory note, four original-source comparisons, all606 new raw cases, all625 old decompositions, reference-control provenance and actual receipts. Parent source identities match their frozen values.

The adapter uses the correct common orthonormal frame, half-contraction norm and `K=8*pi*G/c²`. It computes pressure scalars in J/m³, signed dimensionless component stresses using the same instantaneous H, and `Pi_total=abs(signed_Pi_m+signed_Pi_r)`. The recorded anisotropic-work terms are the separate `-6*(s/H)*p_i` contributions per unit x, not direct collisional exchange. Dust anisotropic stress is zero; the massive canonical species supplies matter stress and remains in Einstein feedback. Shared collisionless photon/neutrino energy evolution remains valid.

The amplitude inversion is bracketed in the original positive-distribution interval [-1,2] and verifies actual initial fields. All600 new pure-matter rows have k=0. Existing neutral controls retain their actual tiny radiation offsets rather than being relabeled exactly zero. The theory note explicitly treats the matter-era dilution formula as an interpretive approximation; the actual mixed trajectories use the coupled original-source RHS.

## Independent raw audit

| Check | Observed result |
|---|---:|
| New complete trajectories | 606:600 matter +6 mixed |
| New saved samples checked | 39,390 |
| Existing histories decomposed without ODE | 625 |
| Existing saved samples checked | 40,625 |
| Original neutral references verified | 25 |
| New physical-axis maximum absolute error | 4.336808689942018e-19 |
| Independent new dimensionless-field reconstruction discrepancy | 2.168404344971009e-19 |
| Independent pressure reconstruction discrepancy | 5.169878828456423e-26 J/m³ |
| Existing signed component sum versus saved total | 4.336808689942018e-19 |
| New saved signed-component sum versus saved total | 0 |
| Four full-source/reduced raw observable comparisons | 1.7031948778173682e-11 maximum absolute |
| Source H² relative residual | 2.220446049250313e-16 |
| Two massive directional-energy relative residuals | Maximum1.4810608772742288e-10 |
| Maximum absolute massive initial amplitude | 0.8275025625756662 |
| Maximum absolute radiation k | 0.18946630461100597 |
| Minimum massive cell population | 5.485187002940815e-31 |

All new arrays are finite, with positive H and E0. Minimum E0 is `0.9998980932241679`; sampled-brightness minimum is positive as recorded in the run summary. Independent reconstruction uses raw states, original canonical helpers and SI constants, without calling the new component adapter to generate expected stresses. The tiny discrepancies are floating-point operation ordering, far below frozen limits.

Every new endpoint binds exactly to its NPZ and CSV. All625 old shared fields remain equal to their original raw values. Every reference control preserves its old JSON/NPZ hashes, initial parameters and source/case identity; the625-row companion table correctly distinguishes600 new trajectories from25 REFERENCE_REUSE rows. Detailed checks are in RAW_AUDIT.json and the read-only audit script.

## Actual cancellation result

The six mixed cases start with individual stress magnitudes .0004 and opposite signs: their sum is zero to roundoff while the sum of their magnitudes is .0008. For the S0=0, positive-matter case, final values are approximately

- signed matter Pi: `+2.2769506379788566e-5`;
- signed radiation Pi: `-9.40362719772204e-5`;
- signed total Pi: `-7.126676559743184e-5`;
- shear magnitude Sigma: `4.908041156489128e-5`.

The reversed initial-component signs give final Sigma `4.907894872787359e-5`. Thus initial total-stress cancellation does not persist under the actual coupled evolution. This conclusion is supported by newly solved mixed histories, not a sum of independent slice responses.

## Plots, resources and recovery

All three PNGs were visually inspected. The matter heatmap has physical axes and explicitly labels600 new plus25 historical controls. The old component plot identifies historical local data and a symlog scale. Mixed panels distinguish signed components from positive shear magnitude. All676 heatmap rows,390 mixed plot-history rows and260 old plot-history rows bind to audited raw values.

The actual new local run completed606 cases with zero failures. Observed worker choices were6,7 and8; recorded run wall was14.977557074002107 s and aggregate child wall16.523054625104123 s. These are budget receipts, not speedup evidence. Reviewed receipts exit zero. Source inspection confirms finite budgets, parent resource observer, single-thread numerical libraries, lower-priority workers, identity-matched resume and no silent retry of failed/unfinished cases. The NCP script passes shell syntax checking and invokes only the new sweep plus plotting; no authenticated NCP run occurred.

Implementation reporting must remain precise: the worker model and energy matrix are reused, but original CanonicalMomentumFV objects and quadrature are reconstructed during amplitude inversion. No cached-construction, measured speedup or memory-reduction claim follows. This is a reporting limit, not a scientific blocker.

## Claim ceiling and next action

This is a finite-model collisionless reflection-even LRS result. Positive canonical populations and sampled brightness do not establish global massless positivity or full quadrature/closure convergence. Native H/He feedback, general non-LRS closure, observational admission, production, and remote64-core performance remain outside scope. No old L/tolerance campaign or optional benchmark was rerun or requested.

Proceed with controller-authorized scoped publication and backup. Any final handoff text created after this review should acknowledge the completed PASS and preserve these limits; it should not reopen the closed numerical gate.
