# Loop1 panel primitive

Exclusive changes: new `src/panel.rs`, `tests/panel.rs`; legacy V2 and production are unchanged.

`Panel { l,r,beta,family,ln_n }` stores shape independently from positive log amplitude. `restrict(a,b)` integrates the actual parent density on the geometric intersection. Right-front subintervals retain the parent's taper, rather than introducing an artificial zero at an interior cut. Exact geometry-empty support returns None. Invalid/reversed/nonnormal arithmetic is rejected. Parent widths are admitted using TwoSum exact binary64 endpoint differences; clipped integration pieces may be narrower than the parent-width minimum.

The normalized local mean is evaluated directly as the positive weighted average of `expm1(d*t)/expm1(d)` on t∈[0,1]. This avoids extracting shape by subtracting lnM-lnN or nearly equal ordinary moments. The corresponding mean-exp and eta node are derived from that normalized shape. A one-ULP interval has no representable interior node; `Restriction::quadrature_node()` rejects that stock rule, while the restriction and its positive log fraction remain valid. Thus moment-exact refers to the real-arithmetic rule, not a universal binary64 node identity.

A positive Gauss8 composite rule doubles through2,4,8,16,32,64,128 panels. Stopping requires both relative normalization and absolute normalized-mean successive differences≤2e-14. The 128-panel candidate uses1024 distinct nodes per integral; it streams these without storing vectors. This is an empirical convergence indicator, not a rigorous interval error bound. Counts/moments are never repaired using a residual or posthoc normalization of owner weights.

Failure record:

- `/usr/bin/time` missing: environment failure before any test process; preserved RED.time.
- An explicit unsupported primitive stub produced6 expected assertion failures; this is new-feature RED evidence, not proof that an existing legacy routine implements the wrong API.
- First64-panel convergence cap rejected beta±128, including right-front128. The diagnostic showed 32→64 relative normalization change5.96e-13 in that front case. Extending to128 retained the2e-14 threshold and original5e-13 oracle target. Both failed candidates remain as logs/source; this was not a tolerance relaxation.
- mpmath absent in both default and primary interpreters: two environment import failures retained. Independent analytic exact-binary-input oracle uses stdlib Decimal160 instead, with distinct antiderivative formulas and no candidate quadrature reuse.

No gas evolution, moment-fitting beta inversion, projected multistep representation, tail owner dynamics, or production exporter is implemented by this module. The finite positive log amplitude is consumed unchanged apart from the restriction's log fraction. Ordinary floating-point arithmetic error is separate from tail readout-loss bounds.

Resource qualification: initial stub compilation and diagnostic compilation were not timed; compile totals cover timed compilations only. All numerical test/probe/oracle launches, including failures, have receipts. No runtime speed claim is made.

Independent-review correction: the first implementation returned a single rounded `ln_n + ln_fraction`. At parent log count−1e12, a half-panel's log correction lost about3.19467e-5. The final restriction carries an unevaluated TwoSum pair `ln_n` (high) and `ln_n_lo` (low); `log_amplitude_parts()` is the authoritative interface. Consumers must not round this pair back to one scalar before owner propagation. The supplied parent still has one exact binary64 input log; general paired-parent feedback and repeated projection remain separate integration gates. The added602nd oracle fixture targets this defect, and the final checker tests all602 amplitude pairs using Decimal(hi)+Decimal(lo).

Subnormal geometric pieces are explicitly unsupported, independent of positive tail amplitude. Review witness parent[-1,0] RightFront, cut[-2q,-q], q=smallest subnormal, gave old normalized mean5/12 rather than4/9 (error1/36). The new guard requires normal positive piece width, stretch and taper scale; it rejects instead of inventing empty support. The original normal one-ULP restriction near1 remains admitted; its stock node still rejects. Nine final native tests pass.

Loop2 extension (after independent loop1 admission): Family::LeftFront uses the actual y exp(beta*y) interior profile with zero lower trace. Its restrictions retain the original parent taper, including middle children. No child is retapered or photon moments repaired. Twelve native tests and903 exact-binary-input cases (3612 independent Decimal160 checks) pass. The independent left-family oracle uses the first exponential antiderivative moment, not the candidate quadrature. This is a density-family/integration extension, not a source-history fit, beta inversion or a coupled gas result.
