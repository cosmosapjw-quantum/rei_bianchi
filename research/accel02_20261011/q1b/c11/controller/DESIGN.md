# C11 bounded production-controller prerequisite

Status: implementation-verified on new manufactured and binding cases. Actual changed native-controller execution belongs to `../integration/`. No full-history temporal or spatial convergence has been measured by this module.

The original C10 source/absorption/native maps and their checkpoint-bound bytes remain unchanged. This controller receives a versioned step callable and treats source, native, endpoint, domain, and fixed-origin ledger errors as failclosed. Only a measured temporal truncation defect produces an adaptive rejection. This deliberately avoids an implicit loop of shrinking around a source-precision failure.

## Derivation and numerical norm

For a first-order smooth map, a full step has local error `C h^2 + O(h^3)` and two half steps have error `C h^2/2 + O(h^3)`. The difference between the two trajectories estimates the fine local error with denominator `2^1−1 = 1`. The accepted trajectory is exactly the two positive half steps. No Richardson extrapolation is performed; therefore the controller does not form negative weights or combine gas states/counters from different histories. The next trial size is `h * clamp(0.8 * error_ratio^(-1/2), 0.2, 2)`, with no growth after rejection.

`CONTROL_V1.json` was frozen before actual C11 native controller execution. Fixed numerical scales are abundance fractions1 (including zero-initialized HeIII), temperature10000K, original H reference density for electron/photon number, rate1e-12/s for all three photoionization rates, original H density for the L1 photon-number distribution defect, and original H density times13.598434599702eV for the L1 radiation-energy distribution defect. They are predeclared numerical units, not inferred candidate maxima. The reference H density was read from preserved C10 output; that output was not recomputed. The local target is2e-7. No scalar floor is added to physical populations, photons, rates or official scientific comparison denominators.

This is an asymptotic local estimate, not a rigorous global error bound. The first-order splitting error may still accumulate or be amplified. The official per-field maximum difference divided by the **same fine subset's own maximum**, separately on the full-history65/129 epoch sets, remains unchanged. A local HeIII relative error near1e-16 does not force a scientific rejection, and a controller pass does not certify the eventual global2e-6 temporal criterion. Full-history matched refinement remains mandatory.

## Events and domains

`next_boundary` uses the supplied hard event or requested endpoint exactly. No `nextafter`, tolerance-shifted event time, clipping, state seed or endpoint interpolation is used. Source redshift knots and source-band/cell birth branch points may be supplied as hard boundaries. Source quadrature continues to split its own pinned table-energy events. For a continuous positive cell measure, a photoionization threshold moving through the cell changes the integrated opacity continuously; it remains a quadrature cut at each evaluation. Support/threshold coincidences require a separately established trace or explicit failclosed rejection. The unresolved physical endpoint contract is not admitted by this controller.

Every full, midpoint and fine candidate is checked by the injected validator. It must check strict physical domains and cumulative ledgers relative to the original IC, not just a local residual. An invalid coarse candidate is not hidden because the fine candidate happens to pass. Forcing an event interval below the declared minimum step produces an explicit failure; the controller never shifts the event.

## API and durable state

- `controlled_trial(state,t1,step,observe,validate,controls)` returns complete coarse/fine diagnostic data and accepts neither a prefix nor a checkpoint itself.
- `run_bounded(...,on_accept,on_attempt,cursor)` caps work with an operation budget. `on_accept((midpoint,fine),compact_trial,prospective_cursor)` runs only after both half boundaries and the local defect pass. The physical input state is deep-copied before each branch, so rejected work cannot mutate it.
- `native_observables(state,provider)` binds the frozen9field+distribution metric to actual native outputs. It observes exact zero trace values and has no denominator substitution.
- The cursor stores `next_step_s`, total attempts, accepted/rejected macro counts, accepted underlying boundary count and the exact accepted clock. `accepted_boundaries=2*accepted_macros` and attempts accounting are checked on restore.

A durable accepted macro checkpoint must contain both newly accepted half-step boundaries in the full prefix, all physical/counter/precision state, the cursor, hard event/output schedule, frozen control/source/binary identities, and the original IC ledger references. Restart is at the final macro endpoint. Restart at an accepted midpoint is not established by this API: it would additionally require a pending already-accepted segment record. A checkpoint write failure aborts before the method returns a newly committed state. A callback can publish an atomic checkpoint; this module itself does not claim persistence.

## Bounded cost and remaining gates

The changed native pilot requested by the frozen control is0→1e10s, initial macrostep5e9s, at most3 accepted macrosteps and6 attempted macrosteps. Thus the maximum completed map evaluations are18 (3 per attempt), with no repeated C10 fixed1/2/4 family. Internal nonlinear/provider calls remain measured by the actual integration runner. Hitting this engineering budget returns `BUDGET_BOUNDARY` with the last accepted state and exact cursor; it does not claim completion. Numerical/source/endpoint failures remain explicit failures with the preserved committed prefix.

An actual native measured cost is needed before deciding whether first-order refinement is impractical. No higher-order map is introduced on the basis of the old tiny-HeIII endpoint relative metric. A positive higher-order or source/absorption-coupled alternative would need its own common pairing, strict domains and independent convergence evidence. This bounded prerequisite can authorize a later full-history attempt only through the requested independent local-GO review, and cannot substitute for that scientific run.
