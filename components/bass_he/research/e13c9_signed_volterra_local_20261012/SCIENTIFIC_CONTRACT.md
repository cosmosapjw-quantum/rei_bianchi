# E13C9 signed second-Volterra local prototype

## Objective and authorization

Continue the unimplemented E13C9 node in E13C8 NEXT_DAG.json. Resolve whether a causal signed second-Volterra correction can give a useful narrower enclosure of the SAME captured OFF finite problem at low additional cost. All theory, implementation, short numerical work, analysis and review are performed here. The user's inherited authorization covers additive GitHub draft delivery and backup writes; no merge or force push.

This is a new numerical representation of the fixed finite solution, not a change of gas evolution, source, closure, branch, capture or physical model. Original 2,331-path NCP work and E13C8 full reduction are complete and are not replayed. Full finite E13C8 admission remains in force; any E13C9 numerical admission is limited to the actual selected paths. Physical, continuum, production and receiver remain HOLD.

## Fixed source and inputs

- Original E13C7 source lock SHA-256: 386d0abd02a33b15a015166369cec981b00fd05987dbd146f2badcb9f604688f.
- E13C8 complete ZIP SHA-256: ba4b1ace541f52bae5dd096d3da75ca9f0bf2d1894d0c3cba40375e40b1eca80.
- E13C8 reduction semantic SHA-256: d647ba154b84baf22a3f85f9b7dca19f029b97f466838c036a9d3321f4c315d1.
- Source is the restored original package, verified by its manifests and Context source gate. The three inherited interval/coefficient/path modules remain byte-identical.
- Selected nodes: 1 (ordinary HI, largest saved D), 1162 (HI+HeI), 1976 (all species), 1620 (HeII mask event), 2344 (source event and exact-zero prefix). These have 12 segments in total. Baseline N is 1024 for nodes 1, 1162, 1976 and 512 for 1620, 2344, at P60.
- Cached local.signed and local.bounds are independent of incoming correction. Verify cache bytes, source lock, path-input identity, work N/P, segment order and original kernel identity before reuse. Recompute S and incoming gains from the NEW carry; never reuse the old S or outgoing radius.

## Definitions and numerical method

On a segment u in [0,h], P_f'=q_f-Lambda_f P_f, P'=q-Lambda P. delta=P-P_f, r=(q-q_f)-(Lambda-Lambda_f)P_f. Initial delta(0)=c+e, |e|<=eta. F(u)=exp(-Lambda_f u), Kz(u)=integral_0^u F(u-v) DeltaLambda(v)z(v)dv. delta1=F c+F*r, delta[2]=delta1-K delta1.

Exact remainder: delta-delta[2]=(I-K)F e+K^2 delta. D>=integral|DeltaLambda| is a whole-segment norm bound; S=|c|+eta+B_r bounds the true delta. Endpoint residual <=(F(h)+H_h)eta+H_h D S. Moment residual <=(|G_i|+T_i)eta+T_i D S after adding integral k_i delta1. No D<1 assumption is needed. Endpoint H_h is never substituted for D.

Use normalized x=u/h, a=h Lambda_f. Obtain delta1 prefix endpoints by the exact attenuating recurrence with a validated local midpoint forcing integral. A whole-cell range encloses delta1 inside each cell. Integrate signed k_i delta1 by directed whole-cell rectangle intervals. All constants remain exact lifts of captured binary64 values. Decimal directed precision P60 is inherited. M_second=32,128 controls only the new correction; it does NOT change or recompute baseline first-variation quadrature N_base. Rectangle enclosure generally has first-order width convergence; the Volterra [2] index is not a claim of global discretization order.

## Protected scientific meanings

Preserve OFF mode, all captured gas interpolation, source flags, species masks, cutoff versus binding-energy distinction, weights, initial data, exact photon stitch, signed energy seams and all species moments. Time is dimensionless log-scale-factor displacement; photon stock/number and eV-weighted energy/heat units are inherited. Do not clamp known microscopic branch discrepancies at nodes 1620/2344. No invented input, hidden intersection, old-interval fallback, precision relaxation or clipping. Totals used for comparison are exact species interval sums as in common.new_metrics.

## Work and completion bar

1. Derive and implement the O(M) causal correction with source-bound cache reuse.
2. Execute small exact/manufactured controls for signs, zero total coupling with nonzero species defects, forcing, nonzero incoming uncertainty, and prefix containment.
3. Run M32 then M128 on the five declared paths, with 60-digit intervals. Perform any necessary in-scope repair only after preserving first failure and diagnosing its cause, into fresh outputs. No blind automatic reruns. A further resolution/precision check requires a concrete unresolved risk.
4. For local numerical admission require all 34 per-path raw metric intervals nested and nonincreasing against their own admitted baseline, exact ledgers containing zero, and independent non-author decision. Aggregate selected-path P and H width reduction of at least 10 percent at M128 is the predeclared useful-improvement target, not a physical tolerance. If a candidate fails, retain the raw result and HOLD/REWORK without intersection.
5. Report actual coefficient calls, first-quadrature replays, prefix/correction work, wall time and RSS separately. Compare M refinements as correction-only convergence. P80 is not required unless new cancellation or directed-rounding evidence demands it.
6. Maximum initial local work: 2 levels x 5 paths, per-path wall limit 120 seconds, up to 3 workers and 1 GiB address-space cap per process. Short manufactured controls and read-only reduction/review do not create a bulk physics job. These are local safety budgets, not measured resource requirements.
7. Prepare actual code, evidence, review, complete backup and NCP handoff. A new NCP work list requires a concrete unresolved accuracy question, locally admitted method, remaining long independent work and measured cost evidence. Merely occupying 64 cores or 128 GB is not a goal.

## Evidence and failure semantics

Separate derived identity, directed numerical enclosure, implementation checks, independent decision and physical claim. Cache identity proves bytes and matched definitions, not scientific correctness by itself. Preserve the original E13C8 first failures inside its complete dependency archive and any new E13C9 failures. Unexecuted full-population second-correction is NOT_RUN. Provider attestation and same-work serial speedup are NOT_ASSERTED / NOT_ESTABLISHED.
