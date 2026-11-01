# REI IGM: original-26-event parent-temperature edge science (2026-11-01)
## Authority and objective
Original source-accepted first-canonical-interval state (2026-08-29) at tick 160/131072, 46080 H/He spatial nodes, three named shape lanes. The initial independent-output full-versus-two-half \(\ln T\) upper distance was `2.1245050576368385e-4`, which failed the **unchanged** strict `2e-4` gate. This is the actual first-interval blocker. An element-conserving representative point and successful original nonlinear 26-event full/half step were already established in [PR #328](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/328). [PR #327](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/327) is a related source-T derivative at that representative. [PR #330](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/330) shows two source snapshots are not a jointly valid time integral.

**This unit changes only one dimension of PR328:** the accepted parent `log(T)` is taken at its **actual lower** or **actual upper** bound for every node, while the same nucleus-preserving population representative, original causal clock, original 26-event physics, and original source uncertainty intervals are preserved. Six original 46,080-node runs are prescribed (2 edges × 3 lanes). These are conditional source-inherited point-parent sections, **not** endpoints known to be reachable by one coherent physical source trajectory, not all-X and not a full-interval promotion.

## Derivation and physical budget (derived; Wolfram symbolically checked)
For source H/He per-nucleus fractions and constant nodewise \(y_{He}=N_{He}/N_H\),
\[
x_e=x_{HII}+y_{He}(x_{HeII}+2x_{HeIII}),\qquad
u_{bind}=\chi_Hx_{HII}+y_{He}\{\chi_{HeI}x_{HeII}+(\chi_{HeI}+\chi_{HeII})x_{HeIII}\}\quad[\mathrm{eV/H}],
\]
\[
u_{th}=\tfrac32 k_B T(1+y_{He}+x_e)\quad[\mathrm{erg/H}].
\]
The \(\chi\) values **must** be the locked original REI source-model thresholds `rim.CHI_{H,HEI,HEII}_EV`, not a new NIST replacement. This is the nonrelativistic translational thermal gas budget and chemical binding diagnostic, not the full radiation+escape+expansion energy ledger. Symbolic derivatives:
\(\partial(x_e)/\partial(x_{HII},x_{HeII},x_{HeIII})=(1,y_{He},2y_{He})\);
\(\partial u_{bind}=(\chi_H,y_{He}\chi_{HeI},y_{He}(\chi_{HeI}+\chi_{HeII}))\);
at fixed chemical fractions \(\partial u_{th}/\partial\ln T=u_{th}\). Wolfram returned `{1,y,2y,kh,ke*y,(ke+kee)*y,0,0}`.

Each original full map \(F_h\) and two-half map \(H_h=F_{h/2}(F_{h/2}(Y))\) returns independently outward bounds at a **shared point parent**. For each of seven outputs \(g\) report the source-conditional conservative interval
\([g(F_h)_{lo}-g(H_h)_{hi},\ g(F_h)_{hi}-g(H_h)_{lo}]\)
and center difference; this is NOT the fully coupled state-source \(D_h(X,\Theta)\). Compare lower/upper parent-temperature sections; a finite secant of output centers is a **diagnostic**, not a rigorous derivative bound. Retain the existing 2e-4/2e-3 gates and all failed event receipts, and do not infer statistical significance from 3 repeated lane states.

## Implementation and acceptance
`edge_probe.py` reuses the sealed PR328 original source-archive SHA `a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b`, accepted-state numerical SHA `cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab9999e7e3508a5161edb01`, and original 26-event kernel SHA `579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644` before source evaluation. Population H/He totals are reconstructed exactly from the frozen point's HII, HeII and HeIII. Original four source-evaluation sites and MPRK22(1)+Alexander SDIRK2 are untouched. If a physical edge fails its original implicit/table gate, preserve the failure and classify as a bounded negative result, never overwrite to PASS.

**Expected scientific output:** 6 × 46080 = 276480 *lane-labelled T-edge model diagnostic rows* with per-node parent T, seven signed nonlinear full/half differences and independent upper bounds, plus six source-owner threshold/physics JSON receipts. The original accepted parent still has 46080 unique spatial nodes, not 276480 independently measured states. Failure cases may reduce actual row count; never claim expected rows without CI evidence.

## Original milestone count, ownership and stop
`Central=28/88_REPORTED; Working=33/88_REPORTED; PhysicalFast=4/7_REPORTED; Canonical_Delta=0; FirstCanonicalInterval=BLOCKED_MINIMUM_STEP; Production=HOLD`. Source parents #320/#327/#328 remain immutable, current repo `main` untouched. No merge, force push, source substitution, new budget, tolerance change, or automatic next DAG promotion. Native subagent NOT_RUN (unavailable), and any adversarial review is same-author, not independent.
