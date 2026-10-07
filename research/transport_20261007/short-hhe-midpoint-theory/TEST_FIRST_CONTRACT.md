# Proposed test specification for bounded midpoint H/He coupling

Date: 2026-10-07. This proposed test specification records no numerical history. The existing short H/He coupling results and failed/passing evidence remain unchanged.

## A. Frozen method and inputs

Select V1 of METHOD_DERIVATION.md: four endpoint unknowns; global arithmetic fraction/w midpoint and actual midpoint background for zero-photo provider and all nonphoto owners; segment-centered affine fraction/w state and actual segment-midpoint background for all photon rates/source; unchanged V2 kernel and exact-event anchor. Shared A_i/B_i determine the full photo update. Keep all provider/closure/constants, original config, source spectrum and unit conventions unchanged. Same fixed positive spectral nodes, no projection, no new bins or cutoff repair.

Preserve the original Newton residual tolerance vector [1e-14,1e-14,1e-14,1e-26], 16-iteration cap, relative pivot rule, finite-difference increments, 12-halving strict line search, and no automatic timestep retries. Separate endpoint and stage admission. A changed method signature must not change thresholds or conflate midpoint staging with endpoint output.

Bind executable results to source and input hashes. Negative controls must produce actual failed assertions rather than compilation failures.

## B. Focused unit/algebra tests, preregistered before implementation

These controlled scalar/one-characteristic tests isolate numerical consistency. Where a coefficient is synthetic, label it a mathematical test double, keep it separate from the unchanged physical fixture, and still exercise the actual candidate residual/staging/kernel path. A duplicate toy integrator alone cannot validate the implemented H/He path.

### T1. Stage wiring and endpoint admission (RED for original BE)

- Distinct admitted y0,y1 and a nonconstant prescribed background. Inspect the candidate's actual nonphoto arguments: exactly ym=(y0+y1)/2 and pm=p(sm). Check returned owners were built from the exact same RHS evaluation and dt=h/Hm.
- Include a source/threshold event with a nonsymmetric segment midpoint. Its actual theta is (m-s0)/h; check yseg and p(m). A whole-step-center mutant must fail this test.
- Set compositions so EOS temperatures differ substantially. Verify Tstage=EOS(affine fractions/w), not arithmetic endpoint temperature. For fixed fHe the EOS is a positive fractional-linear function of theta and lies between endpoint T values; use this to bound evaluated accepted stages, while logging trial stages separately.
- Supply an endpoint outside the fraction simplex/provider domain whose arithmetic midpoint is still admissible. The candidate must reject the endpoint and leave state/ledger unchanged. Repeat for a physical endpoint with an inadmissible evaluated stage if an actual provider-domain case exists; do not fabricate an impossible convex-domain failure.
- Perturb y1 in the finite-difference path; both global and per-segment stages must change. A frozen-stage Jacobian mutant must fail.

### T2. Pure adiabatic material and work owner (analytic)

Use the admitted fully neutral, zero-photo/zero-electron limit, for which the unchanged material equation is dw/ds=-2w and fractions are constant. The candidate must return

  w1=w0(1-h)/(1+h),  work=h(w0+w1)=w0-w1.

The exact continuous answer is w0 exp(-2h). Its one-step local defect has leading term -(2/3)w0 h^3. At a fixed finite endpoint, repeated steps have global order2. The original endpoint BE law gives w0/(1+2h) and must fail the midpoint algebra assertion. Choose three or four modest h values in a preregistered resolved window, with expected smooth local error ratio 8 for halving and observed order tending to 3 (e.g. 2.8–3.2 for the last pair if the leading term is measurably above solver/arithmetic noise). The exact invariant uses the existing 2e-12 owner-identity bound; original physical budgets still independently apply.

This control can invoke the real material RHS with no photon stock/source in a test fixture. It does not modify the main immutable manufactured cfg or establish a new cosmological history.

### T3. Coupled radiation variation (not merely frozen opacity)

One-species mathematical law with lambda=k(1-x), q constant, x'=lambda f, f'=q-lambda f. Start with both f0>0 and q>0. Put v=k(1-x0)f0 and g=q-v. The exact local series is

  x1=x0+h v+(h^2/2)[-k v f0+k(1-x0)g]+O(h^3),
  f1=f0+h g-(h^2/2)[-k v f0+k(1-x0)g]+O(h^3).

Use an analytic scalar solution or independent high-precision Taylor derivatives, not the candidate's integrated-owner implementation, for the oracle. A choice such as k=3,x0=0.2,f0=0.4,q=0.1 gives nonzero gas-feedback and photon-evolution terms. Check each quadratic coefficient and shared x+f=x0+f0+q h. Halving local errors should approach ratio8 once the cubic coefficient is resolved. Mutants using lambda(y0), lambda(y1), or h*lambda_mid*f0 must fail. Also test f0=0,q>0: the leading absorbed count is k(1-x0)q h^2/2, which an initial-stock-only photo update misses entirely.

For the energy owner, retain actual characteristic E=E0 exp(-s), and verify the B_i quadratic term including -epsilon E0 lambda_i0 f0. A start-energy weighting mutant must fail the redshift quadratic-coefficient assertion. A midpoint-energy replacement B_i=epsilon E_mid A_i can reproduce the quadratic term, so it must instead be rejected by the unchanged exact kernel-owner/energy-budget identity at a resolved h; do not incorrectly require its quadratic coefficient to fail. Count-mean heat and other independent energy substitutions likewise face exact shared-owner tests. Shared heat+binding must equal absorbed B_i through the original 2e-12 identity bound.

### T4. Time-varying source/background conversion

- Pure source/no opacity on an event-free characteristic: use the original q_s=Q_t/[C E(s) H(s)], compare Q_N and Q_E to independent positive quadrature of the continuous expressions and require smooth O(h^3) local discrepancy. The frozen kernel is not expected to be exactly equal to the varying proper-time source.
- Repeat source entry and exit at a noncentral interior time. For a prescribed smooth gas/background the segment-centered source/opacity quadrature must retain local O(h^3); whole-step background-center and missing/double-H mutants must fail a source Taylor-coefficient assertion.
- Do not overwrite the kernel's source ledger with the independent oracle. Radiation+all owners must remain internally conservative; oracle errors measure consistency only.

### T5. Exact source/CUTOFF events and energy anchoring

Retain all existing event-anchor tests for HI/HeI/HeII, no absorption below CUTOFF, CHI distinct from CUTOFF, exact source-front zeros, and adjacent binary64 times receiving no event identity. Include both source on/off and species-cutoff sequences with nonzero incoming radiation and competing species.

Within and across complete transactions, track per-node energy as well as stock. At each committed boundary compare the preceding kernel U with epsilon*exp(eta-s_boundary)*f used by the next transaction's ordinary start convention; use the existing 2e-12 continuity bound and report measured errors. At an exact HI outflow require the original stock/energy transfer and zero continuing active stock. Include exact-event endpoint cases, nearby non-event endpoints, and ordinary cut points. This is a regression of representation consistency, not permission to repair the next start energy or weaken original budgets. An unresolved or incompatible anchor must reject unchanged state.

The old adapter proves an exact energy anchor within a transaction; it does not by itself prove bitwise continuity when the next transaction reconstructs energy from eta. Report that distinction explicitly. Compare total roundoff drift against original global number/energy budgets.

### T6. Event-local limitation and fixed-event global behavior

Use q=0, f'=−k(1−x)f, x'=k(1−x)f until tau=alpha*h, then zero opacity. With v=k(1−x0)f0, verify the candidate's expected nonzero local defect

  x_candidate-x_exact=(1/2)k f0 v alpha^2(1-alpha)h^2+O(h^3).

This is a passing limitation test, not a requirement to fake local order3. Use alpha=1/3, k,x0,f0 positive and nondegenerate. Exact splitting and segment-centered staging must still preserve all shared conservation identities.

Separately use a fixed finite endpoint and fixed event time to test global order2. Avoid inferring order from arbitrary adjacent-grid ratios when the event phase changes. One suitable preregistered family is event=T/3 and uniform m=1,4,16,64 subdivisions: the event has the same interior relative phase because m mod3=1. Expected asymptotic global error ratio is16 for each factor4 refinement (order2). Keep this tiny scalar test bounded; it is not a new full H/He history. A globally event-aligned variant may be a separate control but must not be confused with the recommended one-chord scheme.

### T7. Domain, gas positivity and stiff limitations

- Mathematical scalar gas sink u'=-k u yields (1-kh/2)/(1+kh/2). Test small kh for accuracy and kh>2 for negative endpoint/rejection; no clipping and no successful-positive-state assertion.
- Add a one-species photo-only test with u0=1-x0, f0>u0 and kh>-(2/u0)ln(1-u0/f0). The midpoint residual has no physical endpoint root; require explicit failure/rejection, not clipping. For example u0=0.8,f0=1.6,kh=3 exceeds the threshold2ln(2)/0.8.
- Photon kernel positivity alone cannot pass the gas test. Initial/final physical endpoints plus every evaluated EOS/provider stage must pass unchanged admission.
- Retain original underflow-tail rejection and cumulative-ledger transactionality controls. Check a rejected trial and a failed final budget leave all arrays, scalars and ledgers unchanged.
- A failed Newton cap, nonfinite pivot or exhausted line search remains FAIL/PARTIAL; no undeclared fallback.

### T8. Shared-owner and omission mutants

Retain all original mutants: wrong fHe; CHI/CUTOFF exchange; count-mean heat; omitted binding, escape, work or signed CMB; source mismatch; rejected-trial mutation. Add endpoint-owned work/CMB paired with midpoint gas, mixed H factors, stage/endpoint temperature confusion and stale radiation stage. Require a real assertion/budget failure for each mutant. Explicitly check

  energy_defect = R_w + epsilon[CHI_H R_HII + fHe CHI_HeI R_HeII
                    + fHe(CHI_HeI+CHI_HeII) R_HeIII]

up to the original 2e-12 owner identity allowance. Budgets must reject even a residual-converged candidate when the original energy allowance is stricter.

### T9. Provider branches and diagnostic owners

Log T ranges and branch masks for each accepted endpoint, global midpoint and radiation segment stage, with nonlinear trial logs classified separately. Explicitly track 5500 K, T/11605=0.8, CI floor selection and the three CE cap masks. Derive stage bounds from the positive fractional-linear EOS where applicable; endpoint evidence does not certify the exact continuous trajectory.

The saved fixture crosses the HeI CE diagnostic switch around190.785 K. Its physical coefficient is continuous but its cap diagnostic owner is indicator-masked. Require all original ce_cap_HeI_E tolerances and exact zero reports, but do not require uniform order2 for this jump diagnostic. Include a mathematical jump-owner control showing O(h) event error if the jump is unsplit. If any material physical RHS discontinuity is crossed in the actual candidate, narrow the convergence claim or require a separate event-localization specification; do not change provider formulas or hide the branch.

## C. Bounded end-to-end numerical experiment, conditional on units passing

No run is performed by this theory document. The bounded numerical comparison requires the following evidence:

1. Reuse the exact short interval s0=-ln13 to s0+0.0002, the identical source/config/provider hashes, fixed support and declared eta edge union. Retain Gauss2/Gauss4, declared128/256/512 base-resolution A quadrature checks, original4096 distinct-node maximum, and the original exact-event anchors.
2. Preserve four output phases0,1/3,2/3,1. Phase histories have3,6,12,24 transactions for m=1,2,4,8; endpoint-only controls have1,2,4,8. Never rename these as equivalent schedules. Compare all original37 fields at identical saved phases with the original allowance and the0.1 retightening factor. Keep all original budget gates at every candidate and exact zero tables.
3. Preregister smooth order indicators for work_E, cmb_reservoir_E, escape_E, rr_HII, x_heii, x_heiii and abs_HeII, the seven original failed fields. Expect improved second-order asymptotic behavior when the smoothness/event assumptions and noise separation hold; do not force a fit or redefine the temporal-pass gate. Report actual successive differences/order fits, including cancellations or non-asymptotic behavior. Failure to pass any original gate remains PARTIAL even when fitted p≈2.
4. Independently check spectral quadrature at unchanged component1e-6 and kernel/oracle3e-12 bounds. Spectral agreement and conservation do not establish temporal accuracy. Conversely, varying the spectral grid during a temporal fit destroys a pure-time comparison.
5. Obtain a genuinely admitted independent continuous-source Radau reference pair on the identical fixed eta grid and original output phases. The saved1e-11/1e-14 reference is admitted; the preceding1e-10/1e-13 result failed its original number gate (ratio1.0189) and cannot form a certified pair. Use the already admitted1e-11/1e-14 saved baseline after verifying identical physical inputs, exact eta grid/nodes/weights, output coordinates, reference implementation and admission evidence by hashes, then compute its new1e-12/1e-15 companion. Reuse avoids a redundant unchanged integration; a mismatch means the pair is not comparable and requires a separately admitted baseline. Both must pass their original accepted-state number/energy gates and their mutual difference must pass the original0.1 field-retightening gate. If either fails or is infeasible, report reference retightening UNVERIFIED; do not repair ledgers or treat attempted integration as reference certification. Reference agreement is a different-discretization check, not the candidate's pure-time order proof.
6. Read-only independent review must inspect frozen final source, real red/green logs, event and branch evidence, original37 field tables, accepted-step budget traces, resource receipts and reference-pair admission before any scoped PASS. No projection/export-onset or long-history/production claim follows.

## D. New resource accounting (do not retroactively rewrite old evidence)

The old4096 cap was checked only for distinct spectral abscissae. Independent review establishes that old plus returned2440-node arrays already hold4880 values, exceeding a strict stored-values interpretation. Preserve this historical resource limitation; do not relabel the old run as passing that stricter cap.

The new experiment uses a distinct accounting definition: <=4096 distinct quadrature abscissae, <=512MiB process address space, <=32MiB outputs, with measured/recorded concurrent array counts. Physics and accuracy gates do not change.

For this new experiment define separately:

- N_eta: distinct live quadrature characteristics, capped at4096 as before.
- Scalar slots: every simultaneously allocated spectral-density array, including old, candidate, base residual evaluation, finite-difference evaluation, line-search evaluation, reference vectors, and integrator work arrays. Report peak vector count and peak scalar-slot count explicitly; do not relabel4096 nodes as4096 total scalars.
- Allocated bytes/process peak RSS/address-space use: keep the512MiB address-space cap; conservatively bound both Rust and independent Radau working storage, whose multiple state/solver vectors may coexist on the same abscissae.
- Streaming segment stages: yseg and per-node owners may be O(1) temporaries; do not pre-store all per-node/per-stage histories merely to obtain diagnostics. Log bounded summaries plus selected fixtures, not huge internal traces.
- Resource measurements distinguish numerical execution from compilation and include all build artifacts in the32MiB output cap.
- The new bounded experiment has a separate120CPU/180wall numerical budget. Historical receipts remain unchanged. Compilation is separately timed; all numerical probes and independent controls count against the new budget.

The new definition explicitly permits multiple arrays over the same4096-or-fewer abscissae within memory limits; it does not impose4096 total simultaneously stored scalar values. The old stored-values interpretation remains exceeded and is not retroactively corrected.

## E. Completion and stopping

Theory completion: independent review confirms the residual, smooth-order derivation, shared identities and stated limitations; see REVIEW.md.
Implementation experiment completion: all declared unit tests, original physical/domain/N/E/spectral/temporal gates, admitted reference pair, resource limits and independent review pass. A missing gate is PARTIAL/UNVERIFIED, not PASS.

A bounded result does not establish long histories, production integration, projected export, provider changes, or a different solver. A failed gate, exhausted resource bound, or unvalidated numerical-scope change remains a limitation.
