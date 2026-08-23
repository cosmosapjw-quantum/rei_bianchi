# RESEARCH_STATE

PROJECT: REI Bianchi ODE Physics-Specific Remediation Research Loop
VERSION: 1.0
CURRENT_PHASE: phase_10_closeout_complete
LAST_UPDATED: 2026-08-23

## Primary question

PRIMARY_RQ: At repository HEAD `111b6ace750e36e218df7fc9626c6bad2ec19971`, which physics-specific remediation architecture, seeded but not established by the preceding physics analysis, can credibly mitigate the in-scope ODE solver blocker families while preserving H/He population realizability, photon and energy ownership, physical boundary states, table-event topology, and scientific claim integrity; and what minimum decisive verification is still required before implementation or scientific promotion?

## Subquestions

- SQ1 — State geometry and kinetics: Can closed-cone conservative H/He reaction variables, structural zeros, and explicit vacuum/trace regimes remove coordinate singularities and cancellation without changing the physical model?
- SQ2 — Implicit solve and certification: Can production–destruction/M-matrix structure, physics-derived sparsity/low-rank coupling, and genuinely outward-rounded verification make stiff stage solves both robust and certifiable?
- SQ3 — Error and observables: Which independent physical balances, continuous defects, and QoI-weighted error measures can replace self-cancelling ledgers and full-versus-two-half-step distance as scientific admission evidence?
- SQ4 — Hybrid dynamics: Can physics-defined event functions, all-root localization, conservative rollback, and restart maps preserve branch/table topology through grazing, simultaneous, and repeated events?
- SQ5 — Operational scientific validity: What independent reference lane, typed admission contract, resource bounds, and compatibility-versus-corrected-physics split are required to prevent runtime, resume, provenance, and false-success blockers from contaminating physical conclusions?

## Scope

IN_SCOPE:

- Current checked-out code and tracked stage artifacts directly governing the adaptive H/He thermochemistry history, implicit stage solves, interval/certificate logic, event handling, physical ledgers, controller admission, and reference/runtime claims.
- The previously proposed physics-specific remedies only as seed hypotheses: conservative reaction-cone coordinates; structural zeros and explicit vacuum/trace charts; physics-derived production–destruction and low-rank Jacobian structure; independent photon/energy/particle balances; defect/QoI control; hybrid event localization/restart; and separate forensic-compatibility and corrected-science lanes.
- Primary literature, standards, or official documentation needed to test those mechanisms and their stated limits.
- A maximum of six distinct hypothesis families and a maximum of two serious candidates for detailed validation.

OUT_OF_SCOPE:

- Editing repository code, tests, gates, manifests, receipts, scientific results, baselines, conventions, or tolerances.
- Running a production trajectory, reopening a sealed stage, unblinding, publishing, pushing, merging, resealing, or claiming endpoint/publication authority.
- Treating prior analysis, static receipts, same-code parity, green tests, or a segment benchmark as independent scientific validation.
- Purely mathematical, algorithmic, or coding remedies with no explicit physical invariant, mechanism, regime, or observable coupling.

## Terms and conventions

- Physical population state lies in a closed cone/simplex: H I and H II are nonnegative with fixed hydrogen inventory; He I, He II, and He III are nonnegative with fixed helium inventory. An exact zero is a physical boundary/structural state, not automatically a positive numerical floor.
- Thermal/internal energy and temperature use their model-defined positive domain; a true vacuum or vanishing carrier inventory must have an explicit regime rather than being passed through a logarithmic chart.
- Photon number, absorbed energy, heating, and reaction ownership are distinct ledgers. Conservation evidence must be recomputed from primitive fluxes or an independent representation, not from algebraically complementary quantities produced by the same path.
- A table event is a change in physical branch/topology and therefore part of the hybrid model, not merely a controller warning.
- `SUPPORTED`, `PARTIALLY_SUPPORTED`, `CONTESTED`, `UNSUPPORTED`, `MISATTRIBUTED`, and `INFERENCE_ONLY` are claim-audit statuses. `PROMOTE`, `HOLD`, `REJECT`, and `REOPEN_*` are decision statuses; none imply implementation or scientific closure.
- Repository evidence is bound to exact HEAD and path/line fingerprints. Literature facts require directly checked primary sources; reasoned applications to this code are labeled `INFERENCE` or `HYPOTHESIS`.

## Allowed evidence and claim requirements

- E1: exact current-source excerpts, executable read-only counterexamples, tracked artifacts, and repository status/identity receipts.
- E2: original research papers, primary numerical-analysis papers, authoritative monographs where an original source is unavailable, and official library/runtime documentation.
- E3: independently derived dimensional, conservation, limiting-case, regularity, realizability, and counterexample checks.
- Core mechanism claims require at least one direct primary source plus a code-specific applicability analysis; code-defect claims require exact current-source evidence or a reproducible counterexample; promotion requires no fatal validation issue and a feasible discriminator.
- An absent source is recorded as a gap. Citation presence alone is not support.

## Hypothesis status

ACTIVE_HYPOTHESES: H-001 active-face verified hybrid structure-preserving solver; H-002 dual-lane independent physical admission/custody. These are the only two serious candidates. H-003/H-004 are held for evidence; H-005/H-006 are rejected as complete remedies.

PROMOTED: H-001 and H-002 only as `SPECIFIED_RESEARCH_ARCHITECTURE_ONLY`; neither is implemented, validated, production-admitted, or scientific closure.

ON_HOLD: H-003 complementarity/index-1 active-set DAE; H-004 asymptotic/equilibrium regime reduction.

REJECTED: H-005 minimal interior patch as complete remedy; H-006 generic solver switch/same-code refinement as physics-specific closure.

## Blockers

KEY_BLOCKERS: All 32 frozen issue families are cross-mapped (`10 P / 14 A / 8 S`); claim–source audit and the single independent review round are complete. Current fatal evidence includes the He II limiting-factor defect, signed-sum noncontainment, two bounded Krawczyk helper/consumer false-certificate witnesses, non-independent ledgers, disconnected event/restart and low-rank utilities, and live-runtime mismatch. H-001/H-002 remain unimplemented designs.

MISSING_EVIDENCE: A proved active-face nonautonomous PDS construction; qualified outward-rounded elementary functions; continuous trajectory enclosure/defect evidence; hybrid all-root/grazing/restart guarantees; measured block-plus-low-rank rank/conditioning; an independent reference implementation; and owner-authorized quantitative physical/QoI budgets.

## Approval boundary

Continue with read-only source inspection, web research, analysis, isolated temporary state updates, and independent reviews. Stop before repository/original-file writes, convention or tolerance changes, production execution, external sharing, scope expansion, implementation, or scientific promotion.

## Gate

CURRENT_COMPLETION_BAR:

1. Every subquestion has current-code evidence and a primary source, or a named evidence gap.
2. Every core claim has an audited support status; unsupported/misattributed claims are not premises.
3. Every in-scope blocker family and physics seed maps to a hypothesis, rejection, or unresolved gap.
4. At most six distinct families each have a competitor, discriminator, and fatal vulnerability.
5. At most two serious candidates receive independent adversarial review, relevant physics/math validation, and a nine-field decisive verification design.
6. A reviewer independent of candidate generation records the external decision gate.
7. Only promoted candidates are formalized; all six state files and a compact outcome are complete.
8. The target repository remains byte-for-byte unmodified in tracked content and retains only its two pre-existing untracked bundle paths.

NEXT_GATE: New separately authorized work unit only: freeze/sign the two pre-code specification packets before any implementation.

NEXT_MINIMAL_ACTION: No action inside this closed research loop. Preserve the package and do not infer implementation/scientific authority.
