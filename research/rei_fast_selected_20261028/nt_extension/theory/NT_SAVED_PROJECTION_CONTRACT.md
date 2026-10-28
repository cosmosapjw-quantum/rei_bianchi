# Frozen actual saved n/T projection — current executable contract

2026-10-28. **This supersedes the executable plan in NT_FROZEN_CONTRACT.md.** Full canonical binaries have been recovered, so no new response kernel or manufactured interval is needed. Its integrating-factor derivation and physical source discussion remain theory evidence only. User authorized the n/T loop in parallel; root controls the actual bounded planning/presentation allocation. No new IVP, network solve, quadrature, rate evaluation, recurrence, or historical suite replay.

## Inputs and source authority

`nt_extension/inputs/NUCLEAR_NETWORK_HISTORIES.npz` is the primary output; `NUCLEAR_NETWORK_LOG_RATE_TABLE.npz` and `TRACER_HISTORIES.npz` remain immutable corroborating inputs, not additional histories to splice. Exact full blob/SHA/byte pins are those in the recovery receipt from fast_other_survey/fast_core_survey; the implementation records those actual pins and refuses a mismatch. Canonical original source is `6a12f386.../research/rei_tritium_production_audit_20261022/`; full immutable identity comes from recovery, not this abbreviated locator.

Read `inputs/nuclear/NUCLEAR_NETWORK_CONTRACT.json`, `NUCLEAR_NETWORK_SUMMARY.json`, and `review/NUCLEAR_NETWORK_DECISION.json`. Existing independent result is PASS_SCOPED for an 18-family, all-bare, instantaneously thermalized, passive-reservoir sensitivity on82 saved backgrounds. Its code writes:

| Key | Shape | Meaning |
|---|---|---|
| case_names | (82,) | Source case labels |
| family_ids | (18,) | Ordered reaction-family IDs |
| species | (8,) | n,H1,D,T,He3,He4,Li6,Li7 nuclear registry |
| x | (257,) | ln(a/a_ref), source clock |
| T_K | (257,) | Prescribed gas temperature |
| elapsed_s | (82,257) | Saved elapsed proper seconds, case-specific |
| nB_m3 | (82,257) | Proper baryon density |
| log_T_n | (82,257,2) | Natural-log propagated abundances in order T,n; Y=n_i/n_B |
| log_fast_source | (82,257,2) | Natural-log supplied fast source in order T,n, Y/s |
| log_forward_reverse_flux | (82,257,18,2) | Natural-log events/baryon/s; direction0 forward,1 reverse |
| log_forward_reverse_cumulative | (82,257,18,2) | Natural-log integrated events/baryon; same ordering |

Validate actual shapes/registries against these declarations. Select **exact case name `quotient_L16_S-0.6_Am0_Ar0`**, expected index0; never silently select another case if absent. Source arrays are read-only. Selected history includes all257 saved epochs, not interpolation of the three C2 sample points.

## Outputs

One two-panel figure, matching CSV, and compact JSON validation/result under `nt_extension/outputs/` or the lower coder's named output directory. Plot1 shows **log10(Y_T), log10(Y_n)** against the actual saved elapsed proper seconds. Plot2 shows **log10 cumulative forward n_beta and t_beta events/baryon**, labeled respectively n→p beta events and T→He3 beta events. Title/caption names the selected case and the conditional all-bare/instantaneous-thermalization/passive-reservoir closure. The left axis is a linear numeric axis of logarithms, not log of log. Keep t=0 on a linear elapsed-time axis, permitting scientific notation. Optional source x or source-derived z can be secondary only if that mapping is explicitly verified; elapsed time is sufficient and must not be relabeled cosmic age.

A small source diagnostic table, not an extra physics run, includes saved DDn/DDp forward fluxes, total fast-source logs, and the forward n_beta/t_beta fluxes at epochs0/128/256. Include `p_n_gamma`, `n_he3_p`, `d_n_gamma` as source-preserved capture/conversion rows when helpful. CSV keeps raw natural logarithms and optionally log10 transforms. All conversions are division by ln10; do not exponentiate tiny values to make primary curves.

Represent -Infinity as source-zero annotation/missing plotted point, retaining the original tagged CSV/JSON value and reason. Reject NaN or +Infinity. Do not introduce fake floors or connect a fabricated positive t=0 value. A nonfinite zero marker is not automatically ABSENT: preserve channel applicability from the contract/bindings. Do not alter source arrays to improve appearance.

**Use log_T_n as stock authority. Never compute inventories by source minus integrated losses.** Existing C9 repaired exactly this issue: event-subtracted neutron stocks could be negative even though positive recurrence stocks were valid. Maximum stock-normalized discrepancies were11.31116929559128 for n and0.018151836070613776 for T; gross-normalized event balance passed. The independently reconstructed cumulative event history is a separate observable. This projection retains that distinction and does not rerun or reopen the old review.

The cumulative n_beta curve counts protons created by beta events; it is not total proton abundance. Likewise t_beta counts He3 daughters, not total He3. Source all-bare nuclear populations do not supply T I/T II partitions or the other17 ionic curves. Keep this as a **separate nuclear diagnostic panel** alongside the17-state ANGTHERM01 baseline; no splicing, addition, or relabeling of backgrounds.

## Minimum verification

One bounded run after root allocation. It loads NPZ with `allow_pickle=False`, verifies shape, registry, source identity, selected case, finite strictly increasing elapsed clock, and absence of NaN/+Infinity. It confirms exact equality of extracted natural-log arrays with the selected raw columns (equal -Infinity semantics). At C2 epochs0/128/256, compare time and log_T_n directly against `inputs/c2/NUCLEAR_SAVED_SAMPLE.json`; require exact equality where both were serialized from the same floats, otherwise max absolute log difference1e-12 with a reported cause. Do not loosen this criterion silently. Required family names occur once, and forward direction indices are taken from source code/contract, not guessed from values.

Check cumulative log event arrays are nondecreasing from -Infinity to finite within ordinary read/roundoff tolerance1e-12 in natural log; do not recompute their quadrature. Check the log10 presentation arrays agree with raw/log(10) to4 machine eps times max(1,abs(value)); tests are presentation consistency, not new physical accuracy. Existing source validity/admission is reused. The figure must visibly show two positive finite-stock histories and two cumulative beta-event histories over the saved domain; an exact-zero initial row is annotated. Any unexpected mismatch stops this bounded unit; raw outputs are retained for one targeted repair authorized by theory/reviewer.

Allowed code: reader, table selector and plotter plus small targeted checks. No broad parameter scan, new solver, synthetic curve, rate fetching at execution time, or generic adapter. Use existing Matplotlib/runtime if available; source reuse requires no installation. Root's resource limits govern runner and render; code authoring itself is not an execution claim.

## Scope and physical result

The retrieved source already demonstrates conditional nonzero n/T production and decay. Existing original refinement maximum0.00484398118851426dex was below its0.02dex criterion; this is **reused source evidence**, not this projection's convergence experiment. Physical neutral-target branches, fast-particle stopping, high-energy source history and energy deposition remain unresolved for an expanded reionization prediction. External photons in this nuclear source have5–60eV support and its photodisintegration inverse channels are support-zero. C2/atomic donor's other UV specifications must not be substituted.

Physical beta routing remains n→H II+e−+anti-neutrino; T I→He3 II+e− and T II→He3 III+e− under spectator-electron idealization. Atomic recombination is a separate process. A/Z conservation and beta electron counts apply to each source reaction; source event-based ledger and positive stocks have their original distinct numerical representations. No new energy partition or heat is assigned by plotting event counts.

**F4 physical source/charge/stopping coupling remains open; conditional n/T saved-history reuse is complete only after this bounded extraction/render and independent read-only decision.** No new original DAG completion: inherited working33/88 and central28/88. Main595.225063/600 NO_MORE_IVPs is unchanged.
