# Proposed tests, reference matrix, and resource specification

Proposal only, 2026-10-07. No four-step execution is reported by this artifact. Midpoint acceptance was pending in this design. All failed and passing earlier evidence remains unchanged.

## 1. Required primitive controls before integration

P0. Verify input identities. Inherited V2 normal-lane fixtures must still pass; known 64/128/256 initial-opacity accuracy failures remain failures.

P1. Closure restriction/moment arithmetic. Independently integrate ordinary and right-front closures at exact binary64 endpoints using high precision. Cover beta=0, beta=-W, beta±128, ordinary/interior/front restrictions, normal values near both exponent extremes, width=1e-7 and neighboring outside widths, unsupported means, and physically empty intersections. Require 5e-13 exact-input normalized-mean accuracy in the inherited lane; the same 5e-13 scaled-mean target applies to exact supplied shared-scale mantissas; log/amplitude and bound checks must be frozen before implementation. Test n_J exp(eta_J)-m_J and submoment sums. Deliberate posthoc weight normalization and a fitted target that uses the generating rather than stored moments must fail.

P2. Front/support mapping. Whole interior taper is positive and tends to zero at the actual right front; replacing only its endpoint value must fail. Split front parent: left child must not acquire a fake zero trace at the interior split. Retain support through source exit, initial lower edge and moving high frontier. Empty gaps cannot be filled by merging. Test narrowly clipped front/sliver merge, no-compatible-neighbor rejection, exact topology, and transparent lower-trace bias explicitly.

P3. Initial/source decomposition. With opacity zero, number and comoving-energy moments survive exactly in real arithmetic; only physical energy/redshift exchange occurs. With opacity present, initial and source transactions added together agree with the joint characteristic formula against an independent oracle, including birth and depletion inside the interval. Each source owner uses its injected frozen-q approximation. Moment-weight versus geometric-weight unit swaps, independently reweighted heat, exact-source-ledger substitution, and count-only remap must fail.

P4. Authoritative tails. Seed normal/subnormal/zero-readout positive states across scales, including log f=-750; continue attenuation over multiple source-free segments and source restart via logaddexp. Compare with independently high-precision exponential-kernel formulas, NOT baseline BE attenuation. Test nonzero weighted contribution underflow despite a normal aggregate, energy before count underflow, empty versus finite-log zero, malformed logs, inconsistent pair/shape, cancellation in logM-logN, and a log-tail state returning to normal under source injection. Tail-only physical export must transfer authoritative owners before clearing active state. Wrong -log1p attenuation, scalar-zero deletion, epsilon floors, residual-assigned owners, and missing underflow bound must fail. Verify conservative N/E bound accumulation and the original budget plus bound; no relaxed tolerance.

P5. Split/merge/project. Check N/M before and after each operation, owners unchanged, and separate endpoint Gamma/heat/L1 projection defects. Split-then-merge is not expected to preserve shape; it must preserve moments within recorded arithmetic error. Test deterministic support/provenance handling and atomic rejection. Check representation rollback if reconstruction fails after a gas root converges.

P6. Nonlinear wiring. Every trial rebuilds all gas-dependent radiation owners with immutable old panel state. Perturb endpoint gas and verify actual midpoint/segment stages change. Keep Newton topology fixed within an attempt; any restart follows a separately specified cap. Include existing wrong-fHe/CHI/CUTOFF, missing work/escape/CMB/binding, stale stages, source mismatch, count-mean heating and rejected-trial mutation tests. Independently verify residual energy defect and endpoint/next-start energy continuity.

P7. Physical frozen-stage diagnostic. Use actual manufactured opacity, source and inherited stage admission on one then four base intervals, with no gas evolution claim. Compare initial/source owner quadrature to independent positive higher-order integration on the same support. Preserve 1e-6 component and 3e-12 kernel/oracle targets; V2's 512 toy-opacity result is not a certificate for this new continuous panel integrand. Include the source-off witness from TAIL_DIAGNOSTIC.md. If it rejects solely because only the normal lane exists, record expected coverage failure; do not alter the physical inputs to secure a nominal four-step pass.

## 2. Conditional four-base-interval coupled matrix

Only after unit evidence, an admitted midpoint method, a validated tail interface, and an explicit resource envelope:

- Domain s0 to s0+8e-4; four base reporting intervals of 2e-4. Freeze endpoints from exact binary64 construction and retain original provider/config/source. Source upper support must extend to s4+ln(Emax); reusing a one-interval grid truncates new photons.
- Preserve the original 37 fields and allowances and exact-zero fields. Save at least every base endpoint plus original thirds within each base if that schedule is adopted. Include all accepted substeps in physical/budget tests. State the actual number of nonlinear transactions, rather than calling four macrointervals four solves.
- Freeze the first temporal sequence only after the pending midpoint result identifies an admitted regime; do not assume m1 or m8 passes. No automatic 16/32/etc extension follows this proposal. A refined every-step-projected sequence measures the total discretization. A fixed-projection-epoch, unprojected-substep control isolates time error. Preserve the 0.1 original-allowance tightening criterion and all reference-pair admission gates.
- Vary persistent panels with fixed per-panel quadrature, then vary integration resolution at fixed panel state to distinguish closure bias from owner quadrature. Both projected and unprojected-replay lanes need their own admitted quadrature tightening.
- Prescribed-gas-path replay isolates projection accumulation. Self-consistent unprojected replay measures feedback. Keep projection and comparison epochs identical. Independent continuous-time reference on the full 8e-4 interval is an additional distinct comparison, not reuse of the old 2e-4 endpoint.
- Every final projection needs original N/E budgets, its own moment/shape checks, and endpoint Gamma/heat/L1 assessment. A conserved four-step result with failed higher moments is PARTIAL. Exact-zero outflow is required but is not evidence for the later nonzero-boundary test.
- Run one different observation schedule without feeding observations back into the primary state, if within the stated resource envelope. Retightening, geometry, tails, failure rollback and schedule invariance are separately reported gates.

## 3. Resource accounting to freeze before coding

Proposed starting envelope for a primitive/frozen-stage batch: one numerical process and one thread; at most 120 CPU seconds, 180 wall seconds, 512 MiB address space, 32 MiB output including binaries/build; compilation measured separately; all failed attempts counted. These numbers are a proposal, not measured feasibility. The coupled four-interval matrix needs a separate measured feasibility decision within its own total resource envelope.

Define P as persistent panels, C as actual topology-split integration intervals, J as the number of initial-measure subcells per interval, and K as source geometric-rule order. For a streamed residual evaluation the distinct initial/source integration sites are at most C(J+K), before overlap reductions, plus simultaneous closure/oracle sites. A simple panel grid with no extra adaptive cells has C<=P+10 for the ten start/end physical edges, but retained support fragments and adaptation can increase C; count actual intervals instead of trusting the simple bound. Unprojected replay requires historical transformed event/staging edges from its retained paths, so it has a separate measured C_ref; do not apply C<=P+10 to that reference.

Possible nonbinding starting candidates:

- persistent P=64,128,256; stock J=2; source K=4;
- at fixed P=256, owner tightening J=4,K=8 has at most 266*12=3192 stock/source sites under the simple geometry count;
- P=512,J=2,K=4 gives at most 3132; P=512,J=4,K=8 gives 6264 and is inadmissible under a 4096-site envelope unless a separate streamed-concurrency policy is specified and validated. Do not silently reinterpret the cap to admit it.

These are integration candidates, not accuracy predictions. Actual sharp wake resolution, beta admission, front geometry and log-tail overhead may require other refinement and a stop. Do not run all candidates merely because they are listed.

Keep the currently explicit distinction: 4096 distinct abscissae is not 4096 total stored spectral scalar values. Before implementation freeze whether the cap is per concurrently live evaluation or total distinct sites for an entire run; dynamic rebuilt sites make the latter much larger. For this proposal the natural interpretation is simultaneously live distinct sites, with lifetime and buffers instrumented. That is a proposed definition, not a reinterpretation of past specifications.

Report separately:

1. Persistent P, support fragments, raw/scaled/log moment scalars, closure parameters and tags.
2. Old state, base trial, finite-difference trial, line-search candidate, and checkpoint state that coexist. A streaming residual can discard unused trial radiation arrays after extracting residuals, but this optimization must be shown by actual live allocation measurements.
3. Current initial/source abscissae/weights, cached closure statistics, source-event arrays, quadrature/refinement stacks, and high-precision oracle nodes. Closure quadrature cannot be called afresh inside every density evaluation without accounting for its cost.
4. Replay gas-path descriptor count T, shared or copied topology, and whether temporary densities/owners for T stages coexist. Replay at one eta can stream through T stages; retaining all node-by-time arrays is a different memory/cost profile.
5. Nonlinear residual evaluations, finite-difference evaluations, line-search trials, retries/restarts, total characteristic segment calls, and total integration/reconstruction evaluations. Four gas unknowns do not imply four evaluations: the inherited 16 Newton iterations with four FD columns and up to 12 line-search trials can cost hundreds of full radiation evaluations per accepted step.
6. Compiles versus numerical CPU/wall, per-process and process-tree RSS/address space, directory bytes, emitted log volume and all failed attempts. Stop before launching a command that cannot fit the remaining budget.

The projected lane costs approximately O(T E C(J+K) S), with T accepted transactions, E residual evaluations per transaction, and S event segments per characteristic, plus reconstruction/root and oracle costs. Fresh-point unprojected replay has an additional history traversal: at transaction n, input replay costs O(n C_n(J+K) S), plus current-trial evolution O(E_n C_n(J+K) S). Input replay can be cached across Newton trials only when its nodes and prior accepted gas paths are fixed. The total can therefore be O(T^2 C(J+K) S + T E C(J+K) S), or O(T^2 E C(J+K) S) without that reuse. Shared path descriptors save memory, not those history calls. These are operation-count guides, not a runtime measurement. More temporal microsteps also mean more projections in the operational lane and more replay history. V2's fast isolated primitives or the old one-interval midpoint cost do not establish four-interval performance. No full-history Radau/BDF reference or production integration is established by these cost estimates.

## 4. Required completion report and stopping conditions

Report PASS only for the gates actually executed and independently reviewed. Provide immutable input/source hashes, raw failed/green logs, exact acceptance denominators, moment and tail audits, resource receipt, and an artifact-bound independent review. Preserve original field tolerances: fractions 1e-6+1e-3 abs(ref); Gamma 1e-22+1e-3 abs(ref); energy 1e-20+1e-3 abs(ref); photons 1e-8+1e-3 abs(ref); T/Tcmb 1e-6+1e-3 abs(ref). Tightening uses 0.1 of these, without waiver for tiny fields or non-smooth diagnostic masks.

Stop with a precise PARTIAL/blocker for unsupported tail shape/arithmetic, nonrealizable/narrow support, unresolved exact events, failed owner/accuracy gates, exhausted solver or resource caps, an unadmitted reference pair, or an unvalidated change of numerical scope. No successful bounded control implies general coupled histories; no four-step result implies real-boundary export; no finite export control implies the long-history certificate.
