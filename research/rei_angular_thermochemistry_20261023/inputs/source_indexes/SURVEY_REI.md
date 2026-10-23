# REI current-source survey — 2026-10-23

## Result and scope

The current REI continuation should reuse the completed PR221 local operators and local flows, the PR222 zero/tiny-stock construction and D10 saved-history result, and the existing C13–C16 directional photon transport and work equations. A new finite synthesis with the latest C22 event/heat owner can be useful, but directional Bianchi photon propagation, UV stress, gas heating, and expansion/shear work already have implementations and scoped numerical evidence in this repository.

This lane performed **read-only remote intake and local source preservation**. It did not rerun a scientific diagnostic, start an IVP, access NCP, create a checkout/worktree, or write to GitHub. The restored local directory has no Git metadata; its remote identity was obtained through exact-SHA API reads. The parent controller handles conversations, adjacent repositories, backup discovery, the selected new theory/coding unit, and publication.

The selected operating rule is **physmath intrinsic 1.0.0 / approved design v0.2**. Local and exact-current AGENTS.md agree about the personal research trust model, proportional scientific identity controls, existing-checkout default, and Astra scientific contract → lower-tier implementation → fresh independent scientific decision. The old 074933f handoff's version-1.3 wording is historical; the current successor handoff itself explicitly says intrinsic 1.0.0.

## Complete remote enumeration

| Collection | Request and pages | Rows | Terminal evidence |
|---|---|---:|---|
| Branch heads | GitHub REST branches, per_page=100, pages 1–4 | 100 + 100 + 63 + 0 = **263** | Explicit empty page 4 |
| Unique branch-head commit metadata | git/commits/{sha}, all unique advertised heads | **260/260**, no failed requests | Every advertised head mapped to its metadata |
| Open PRs | pulls?state=open&sort=updated&direction=desc, per_page=100, pages 1–4 | 100 + 100 + 7 + 0 = **207** | Explicit empty page 4 |
| Closed/merged PRs | Same endpoint with state=closed, pages 1–2 | 14 + 0 = **14** | Explicit empty page 2 |
| Closed/merged updated since 2026-10-20T00:00:00Z | Filter over the complete closed set | **0** | All 14 timestamps inspected |

**REMOTE_INDEX.json** contains every branch name/head, all 260 head dates/messages/parents/tree identities, all 207 open PR metadata rows, all closed rows, and the exact pagination scope. The raw tool responses are saved as branches1–4.json, openprs1–4.json, closedprs1–2.json and head_{SHA}.json with requested URL and actual fetch timestamp. There are 16 branch heads whose commit dates are on or after October 20. Branch enumeration is exhaustive; semantic source review is targeted to the scientific continuation, not every file of every branch.

A recursive request for the entire PR222 tree returned a transport-closed error. That failed response is preserved. The task continued through successful nonrecursive root/research trees and targeted unit trees/files, without a broad source archive download.

## Current heads and parallel work

| PR / purpose | Current exact head | Commit date UTC | Current interpretation |
|---|---|---|---|
| 221 coupled isotope/local flows | 73c5e00cac26b4efc782446975bd6b6762555997 | 2026-10-22 22:34:12 | Latest advertised branch head; final delivery metadata, science source unchanged |
| 222 orchestration/C3/D10 | b4b5d289aaad9ef167f683f19418b0ff87ed8425 | 2026-10-22 17:53:23 | Successor orchestration DAG and actual completed D10 |
| 219 nuclear/provider foundation | 6a12f3865d9ea427c1391c41caed8bb7cb7ec00d | 2026-10-22 03:23:54 | Scoped source/implementation/delivery foundation |
| 220 compact H–He–Li pilot | 8be7533cc97b3302bf42608699d6e8313ed6af8a | 2026-10-21 16:18:01 | Completed 127-case compact pilot |
| 218 H–He–Li pilot | 4c8794e6e7c4ac553cc85fee728ef9ab6fe81fa8 | 2026-10-21 15:56:17 | Delivered source-bound finite pilot |
| 199 age/exposure D9 | cce008b3fc32c298185b30550b2cd909d74fcd87 | 2026-10-21 14:17:12 | D9 complete; later D10 is on PR222 |
| 217 ACCEL03 | de73c5d6c7bd3498571e9226298040d8259e1acf | 2026-10-21 13:56:37 | Split-stress sweep analysis delivery |
| 215 ACCEL02 | 926bae816ef8339137e2813cc40f1d514b763e1f | 2026-10-21 13:08:31 | Reflected native massive moments |
| 198 LRS V14 | 8bd35af5f11c7ea5945b656be1c013d1c1933498 | 2026-10-21 06:49:51 | Physical birth and later source-preserving delivery |
| 210 BRPERF01 | e4c8133288614638792888367ca10b2ded3138ff | 2026-10-20 10:46:21 | Opt-in rate sharing and photon persistent-pool implementation |
| 211 RUN19 | c9deb933761a8d2593d1176aee028cd423bdbc05 | 2026-10-20 07:29:37 | Rate/native optimization delivery; source investigation only if selected |

All these PRs are open/draft in the observed collection. PR220 had the latest PR **updated_at** value, 2026-10-22T23:13:37Z, while its commit is from October 21. PR update ordering must therefore not be treated as scientific source ordering.

### Branch relation and safe additive publication

The exact comparison of PR221 73c5e00… to PR222 b4b5d289… is **diverged**, with PR222 six commits ahead and PR221 five commits ahead of common ancestor c1714f82ea7de15fee230a1a995365970ee6dc02.

PR222 does not contain PR221's rei_coupled_isotope_sandbox_20261022 and rei_coupled_local_flow_20261022 directories. PR221 does not contain PR222's orchestration, zero/tiny C3 and D10 directories. Moving either branch to the other would discard independent history.

For new work using the latest local isotope/thermal implementation, use **73c5e00cac26b4efc782446975bd6b6762555997 as the additive source base** and reference selected donors at exact commits. The parent chooses whether its already authorized existing PR221 branch or a new additive branch is appropriate. Preserve both branches and refresh the actual head immediately before publication. No merge or remote mutation was performed by this lane.

## Completed work to reuse

### PR221: conditional atomic/local operators and local thermal flows

Exact code read:

- research/rei_coupled_isotope_sandbox_20261022/code/atomic.py
- research/rei_coupled_isotope_sandbox_20261022/code/local.py
- research/rei_coupled_isotope_sandbox_20261022/RESUME.md

PreparedAtomic retains 21 independent absolute abundances while sharing identical electronic blocks. It already implements

\[
F(Y)=PY+n_B(q^\top Y-f_{\rm fast})RY,\qquad
J=B+(n_BRY)q^\top,\quad B=P+n_eR,
\]

a fixed-fast-electron Jacobian column, a dense default solve, a checked block/rank-one alternative, and a positive second-order atomic midpoint for its fixed-temperature/fixed-spectrum scope. Rebuilding the rank-one Jacobian would duplicate finished work.

The conditional event module already supplies explicit coefficient statuses, knot-only/default off-grid policy, log-linear interpolation only with a supplied curvature/error bound, integer baryon stoichiometry, zero-aware mass-action derivatives, supplied energy-reservoir ledgers and the particle-count temperature term. Its documented completion is **156 checks plus two separately authorized onset checks**, not a new combined run.

The local-flow science pin is **9620e1fcc4bdda76e0311206f614234926600381**, with final current head 73c5e00…. The local RESUME records **103 checks** for pure-H evolving-temperature Case-A RR and prescribed-temperature beta+RR, and a separate **96-check paired timing invocation**. These are distinct evidence sets. Precision references remain DOP853 under their specific equations; previous timing ranges do not support a universal performance ratio.

Open physical inputs remain named beta electron/neutrino/recoil energy partitions, thermalization/stopping and reservoir escape conventions, and physical charge-state daughter branching where required. Total beta Q cannot be silently assigned to thermal heat.

### PR222: zero/tiny source and D10 are finished

The current authoritative successor is:

- research/orchestration_sandbox_20261023/DAG.json
- research/orchestration_sandbox_20261023/HANDOFF_NEXT_THREAD_KO.md

The older 074933f73743ed10ff98a10db49d1b72696ead4f handoff was read, then superseded by these files where current status differs.

The zero/tiny source pin **20539a00d3fb5dcdb4165b1c90b4d5d5d1f8ebb3**, path research/rei_c3_zero_tiny_source_20261022/local_source.py, computes the scaled source and fixed-scale Jacobian directly from log products. It preserves a scaled \(10^{-230}\) contribution even when the unscaled \(10^{-334}\) event underflows in binary64. This is already tested supplied/manufactured-event algebra; it does not supply missing nuclear branching or heat partitions.

D10 is complete at **67205cb9a9fc3e36b959e584d3e06c74bdfbbf5e**, under research/rei_orchestration_resume_20261023/. SCIENTIFIC_DECISION.md admits the stated collisionless LRS pressure derivation and diagnostic of **35 existing histories × 153 saved epochs**, with **zero new IVPs**. There are 5,168 resolved stress/deformation sign comparisons with zero violations and 187 near-zero unresolved points. These are saved-data observations. The earlier uninstrumented failed materialization attempt means aggregate 60-second budget compliance was not established; the scientific saved-array result remains scoped and reviewed. Do not repeat D10 because an older DAG labels it ready.

### PR220: actual 21-state inventory and compact optimization

Current paths include research/rei_hheli_compact_pilot_20261022/{NEXT_THREAD_HANDOFF.md,evidence/ROOT_ADMISSION_C.json,code/compact_system.py}; all were directly read.

The completed model is non-tilted LRS Bianchi I, z=20→2, 127 compact cases with 193 samples each, 24,511 main history rows, plus two unchanged full62 oracles. It contains

n; H1 I–II; D I–II; T I–II; He3 I–III; He4 I–III; Li6 I–IV; Li7 I–IV,

with electron abundance from charge. The pilot starts with n=T=0, uses prescribed T(z), external 5–200 eV UV, and isotope-electronic equality. Photo/RR/DR and electron-density → Thomson feedback are included. Its massive anisotropic stress is a separate collisionless nonbaryonic component; the common-temperature baryons have \(\pi_b=0\).

The 62→33 restriction is a constant invariant-subspace map \(F_{33}=RF_{62}(Pv)\), \(J_{33}=RJ_{62}P\). Its code checks vanishing odd geometry, zero initial neutron/tritium stock, equal isotope charge fractions and matched electronic rate blocks. Changing isotope-specific rates or these initial conditions requires reevaluating eligibility.

This is an implemented, completed pilot. Its long redshift domain does **not** imply that the external UV inventory, thermal energy and full radiation \(Q^a\) already form the new dynamic-photon/common-temperature closure.

## Directional finite UV is already implemented: decisive code

### Exact source and local snapshots

The small files are preserved under rei_remote/donors/{SHA}/{repository path}. DONOR_SNAPSHOTS.json records path, byte count, SHA256, and Git blob identity. The C13, C15, C16 code and C16 status all match the already observed exact Git blobs. The three inherited gas/recombination files were also fetched and preserved as reference dependencies; this is not a complete runnable donor checkout.

| Function/role | Exact commit | Repository path |
|---|---|---|
| Positive photon characteristics; proper number measure; UV moment map | d7d0e3ad2d6d7cccdfd70df3a0f310df93ec553d | research/rei_c13_live_source_20261015/short_interval.py |
| H/He gas, conservative finite photon absorption | same d7d0e3ad… | research/source07_c10_dynamic_20261015/dynamic.py |
| Case-A RR/DR temperature/escape ledger | same d7d0e3ad… | research/source07_c11_casea_20261015/casea.py |
| Source-locked Grackle coefficient adapter | same d7d0e3ad… | research/source07_c11_casea_20261015/rate_table.py |
| Two-way UV stress / Einstein shear / gas feedback | 435c94308c0cd7b1ba8ff6518246da061f2fc2fa | research/rei_c15_two_way_shear_20261015/c15_coupled.py |
| Independent pressure/shear expansion-work quadrature | af67c5314669492b07cb574170c09f70994974e4 | research/rei_c16_source_energy_20261015/c16_exchange.py |
| Actual six-scenario work/ledger evidence | same af67c531… | research/rei_c16_source_energy_20261015/RESULT_STATUS.json |

C13's metric and exact fixed-Killing pushforward are

\[
ds^2=-c^2dt^2+a^2e^{-2b}(dx^2+dy^2)+a^2e^{4b}dz^2,
\]
\[
D^2=(1-\mu^2)e^{2\Delta b}+\mu^2e^{-4\Delta b},\quad
E'=Ee^{-\Delta\ln a}D,\quad
\mu'=\mu e^{-2\Delta b}/D.
\]

PhotonCloud.drift preserves each packet's NperH. It does **not** attach a second angular Jacobian to an already pushed-forward number measure. PhotonCloud.to_native_chemistry evaluates energy-dependent cross sections and excess-energy moments; chemical_update imports the depleted photon counts.

SourceState.summary computes \(u_\gamma=n_H\sum NE\), \(P_\parallel=n_H\sum NE\mu^2\), \(P_\perp=n_H\sum NE(1-\mu^2)/2\) and \(\Pi=P_\parallel-P_\perp\), with the trace check \(P_\parallel+2P_\perp=u_\gamma\).

C15 Coupled.quantities and Coupled.rhs feed actual UV energy and \(\Pi\), gamma/nu multipoles, and H/He electron density into the current geometry and Thomson rate. Coupled.drift_segment evolves the next photon characteristic and gas expansion with the changed shear/proper clock. Coupled.step performs source/reaction/drift composition. This is actual dynamic directional UV plus gas chemistry, not a plan.

C16 WorkAuditor independently integrates the geometric work on a dense DOP853 path. Per H nucleus, with \(s=\dot b\), it checks

\[
\frac{dW}{d\ln a}
=U_\gamma+2\frac{s}{H}\sum_j N_jE_jP_2(\mu_j)+2U_{\rm th}.
\]

Its RESULT_STATUS reports six actual scenarios, maximum open ledger residual \(8.88\times10^{-15}\) eV/H and maximum independent Gauss8 geometry-work difference \(7.52\times10^{-16}\) eV/H. These published observations were read, not regenerated.

### Why a new C22/21-state finite synthesis can still add work

C15/C16 are restricted to **a=.1999→.2**, with manufactured warm gas near z≈4. The inherited Gas has H/He populations only, source-locked Grackle Case-A rates cover **10,000–24,000 K**, and the MD14 stellar source and escaped recombination energy remain explicit external reservoirs without a complete gravitating stellar/escape EOS history. They do not solve the proposed longer, source-qualified multi-isotope common-temperature inventory.

The defensible new contribution is therefore the **specific composition** of already validated directional geometry/work with the selected latest reaction/heat owner and finite new inventory/history. It is not a new discovery of directional redshift, UV stress or shear work.

The historical C15 display uses \(\Sigma=\sqrt3|s|/H\), while PR220 uses the full Frobenius \(\Sigma=\sqrt6|s|/H\). Reuse the signed \(s\) and tensor first, then report the current norm. This is a convention mapping, not a change in the physical solution.

## Provider and optimization boundaries

PR219 PROVIDER_REGISTRY.json was read at 6a12f386…. RR scalar fit derivatives and DR numerical fit evaluations have scoped restored evidence. DR empirical low-temperature accuracy, cascades and thermal allocation remain separate obligations. The listed Voronov CI rows do not cover the full pilot temperature range; no validated extrapolation is adopted. Missing CX, isotope daughter injection, Li Auger yields on an expanded spectrum and directional/thermal coupling are recorded as exact input/model obligations.

BRPERF01's full unit tree and README were read. Implementations already include 15-coefficient compact temperature tables, same-temperature native sharing, opt-in SIMD/native code and persistent photon evaluation. Its photon test uses 384 source labels, ±shear and frozen gas. Default rate/photon backends remain Direct/Baseline. These bounded results do not establish a universal coupled speed advantage.

RUN19 and V14 current heads/tree metadata were captured, but their complete code/results were not audited. Further old-branch inspection stopped after decisive C13–C16 overlap was established; inspect them only if their specific runtime becomes a dependency.

## Recommended next nodes

1. **UV21_C22_SYNTHESIS — ready to freeze after the adjacent C22 intake.** Bind exact latest source-qualified event/heat code, reuse C13 direction/energy pushforward and C16 work identity, and construct one finite common-temperature dynamic-photon history for the selected inventory. Freeze proper-time units, per-H/per-baryon conversion, photon measure, closure/reservoir ownership, shear convention and bounded reference/reduced comparison. Compare against previously validated limiting cases without rerunning old cohorts.

2. **DIRECT_SCALED_RESOLVED_EVENT_LEDGER — a concrete optional prerequisite.** Current PR221 local.py computes raw exp(log_rate) before source assembly; outer_transform scales afterward, so a raw-underflow contribution cannot be recovered. PR222's direct-log-scaled kernel solves that representation problem but lacks the richer event energy ledger. If the selected synthesis requires such trace events, combine those complementary pieces and check only the changed source/Jacobian/ledger paths. Preserve current ABSENT/UNRESOLVED behavior; the two historical APIs differ there. This node supplies numerical algebra, not missing physical rates.

3. **BETA_THERMAL_PARTITION — source research then finite local extension.** Bind named electron/neutrino/recoil energy and stopping/escape inputs, then extend the completed beta+RR local flow while reusing pure-RR and fixed-temperature limits. Do not spend this unit redoing the prepared atomic Jacobian, zero-stock proof, D10 analysis or optional timing.

Machine-readable adopted/rejected/needs-inspection candidates, these nodes and publication-base advice are in CANDIDATE_INDEX.json. This inventory selects reusable evidence and exposes current dependencies; scientific admission of the new synthesis belongs to its fresh frozen contract, actual bounded execution and independent review.

