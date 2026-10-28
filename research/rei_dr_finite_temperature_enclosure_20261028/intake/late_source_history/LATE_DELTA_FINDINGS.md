# Late source-history delta and disjoint budget reconciliation

Status: **COMPLETE_SCOPED_SINGLE_LATE_DELTA**. Native source-intake agent `/root/current_repo_census`. This additive report supplements the sealed main `DELTA_SURVEY_FINDINGS.md`; it does not rewrite that earlier observation. No numerical, scientific, CAS, plot, or external mutation was performed by this agent.

## Observed publication and read boundary

The controller observed the source-history branch at `ea805aefa8b73a33414e688ead8e5aca3f4296fa` at 2026-10-28T10:58:13Z and requested one final delta-only read. Five actual read-only GitHub queries ran from **2026-10-28T10:59:17.109Z to 10:59:34.478Z**. `QUERY_LEDGER.json` retains exact arguments, returned identities and times. No subsequent live-ref polling is part of this addendum.

The exact commit is dated 2026-10-28T10:53:54Z, with parent/science commit `a727a27b6f19ce59db752488a69ae7a876e689aa`. The containing final receipt identifies draft **REI PR246**, branch `research/rei-source-history-20261028`, based on PR245 `cc17c2481f3f1057062efe0cbfb505114a0e8cfc`. The final commit records publication and preservation metadata over that science parent. Its science tree is `0b78ef78ed714458a97c4b4591af9031c894fc8a`.

| Exact source read at the observed pin | Read range | Returned and locally matched Git blob | Local SHA256 |
|---|---|---|---|
| `research/rei_source_history_20261028/BUDGET_CLOSEOUT.json` | Full file, lines 1–106 | `2238bd1fb7b638a3a8d1c8e735c79b780bb3b9db` | `79c5db56a06daca386659d5298dac0454b3610d181f627265f08148c60e28f3b` |
| `research/rei_source_history_20261028/STATE.json` | Full file, lines 1–99 | `21dce29bcd16d7326fa246322e7ebafff43533cf` | `e077980a5a610db2fc557f49c97c02f31d13657bfaf104cdf1f517681fcfbfe7` |
| `research/rei_source_history_20261028/DELIVERY_RECEIPT.json` | Full file, lines 1–174 | `96e2c34c9d4b63eb0ac16b46a278677ec86f3841` | `2f6444b6a2c77be5518bd0969697ade41860656189e976b92effa3bc181c7f80` |

Exact plain copies, full raw connector returns, the directory result and commit metadata are retained beside this report. `SOURCE_COPY_IDENTITIES.json` establishes 3/3 exact Git-blob matches. The local current unit's `RESOURCE_ALLOCATION.json` (full lines 1–73) and `BUDGET_HOLD_ADDENDUM.json` (full lines 1–94) were also read to distinguish prior reservations, actual costs and the revised controller hold.

## Actual disjoint execution cohorts

PR246's closeout explicitly inherits **19.204540885 planning / 56.217331494 presentation** from PR245. It then identifies three new completed phases, each with one attempt and return code 0. Their exact command paths use `/workspace/scratch/dfc32e6e80f9/research/rei_source_history_20261028/implementation/` and are distinct from PR245's external-source package and our directional `run_once.py`/`plot_saved.py` cohort.

| Cohort identity: package + science commit + published phase + command | Child CPU-s | Observed wrapper CPU-s | Ledger |
|---|---:|---:|---|
| `rei_source_history_20261028` / `a727a27b6f19ce59db752488a69ae7a876e689aa` / `tests` / `test_history.py` | 0.62069 | 0.004044000000000004 | planning |
| Same package/science commit / `qss_diagnostic` / `evaluate.py` | 0.4868 | 0.0033870000000000003 | planning |
| Same package/science commit / `saved_data_plot` / `plot.py` | 1.1919530000000003 | 0.0034389999999999993 | presentation |

The published closeout does not expose native PIDs or per-phase start timestamps. No UUID, PID or stronger runtime identity is invented. These are exact source-reported phase records in a fetched, hash-matched publication, not a fresh independent rerun or OS receipt audit by this intake agent. The one-scope delta request did not retrieve every underlying phase artifact.

New observed phase totals are **1.114921 planning / 1.195392 presentation**. The source separately retains **0.5 / 0.5** new tail reserves. Thus the new disjoint **charged-known-plus-reserve** increments are **1.614921 / 1.695392**, and PR246's own branch view closes at **20.819461885 / 57.912723494**. Measured CPU and unobserved tail reserves are not conflated.

PR246 closes its foreign temporary 30/65 authority and restores original 10/30 policy caps. That authority is not transferred here. Its future three-case IVP proposal is explicitly **PROPOSED_NOT_AUTHORIZED_NOT_RUN**; the suggested main cap700 and reserve100 are not current authority. Main remains **595.225063/600, NO_MORE_IVPs**, with zero new IVPs reported.

## Explicit union without double counting

The controller's already reconciled current view is preserved: common PR243 baseline **17.295332885 / 54.561494494**, plus PR245 disjoint increments **1.909208 / 1.655837** (including its retained tails), plus the independently measured directional cohort **0.134826177 / 1.865714814**. That is **19.339367062 / 58.083046308** before this late delta and before the new DR CAS.

Adding only PR246's newly published disjoint increments yields:

- planning: 19.339367062 + 1.114921 + 0.5 = **20.954288062 CPU-s**;
- presentation: 58.083046308 + 1.195392 + 0.5 = **59.778438308 CPU-s**.

The common inherited balance is counted once. The source-history STATE's stale cross-thread observation that PR244 remained unrun does not erase our actual directional receipts. Its quoted inherited total therefore remains a separate branch view rather than replacing the union.

The controller separately preserves one already completed bounded DR symbolic check: **0.00341 CPU-s observed**, within a **0.05** reservation, with **0.04659** retained unobserved reserve. Therefore the current observed-plus-inherited-closed-reserve view including observed CAS is **20.957698062 / 59.778438308**, and the conservative view retaining the whole CAS reservation is **21.004288062 / 59.778438308**. CAS startup/transport remains UNKNOWN_NOT_ZERO; no whole-session budget PASS is asserted.

The current authorized 20/60 planning ceiling is exceeded by these proved disjoint charges. The numerical and figure worker attempts remain **0** in the controller's hold addendum. Planned numerical0.4+tail0.2 and figure1.5+tail0.3 are reservations only, not executed costs. Including those planned reservations would reach **21.604288062 / 61.578438308**. The proposed 22/62 ceiling is explicitly **not yet approved**. This agent neither executes the jobs nor requests or grants additional authority.

## Scientific source scope and limits

PR246 reports scoped source-history and matched-clock completion, and zero-IC QSS family tracking at **201 saved epochs**, with **200 certified saved epochs per family**, index0 initially uncertified. The record explicitly limits this to saved samples: whole-interval certification is NOT_RUN. Full17 solver preparation is READY_NOT_RUN; the three-case coupled IVP remains pending. Original working33/88, central28/88, total88, delta0 and fast4/7 are unchanged.

The final receipt reports 51 published files, nine selected exact UTF-8 readbacks, a matching PNG Git blob, and completed Drive/Dropbox upload ACKs plus separate metadata sizes for a 951630-byte capsule SHA256 `3cb2b831b849ad05f8b7e7d0dca86b26b2109c847d685b7af595e283a7566054`. This intake read the containing receipt; it did not independently re-download provider bytes or audit all 51 files.

This late publication changes the current budget union and the source-history owner's factual stage status. It does not supply a whole-temperature native DR interval certificate or change the DR source-only review scope. No next-unit selection, new scientific admission, original-gate mutation, physical T/native25/radius inference, or subsequent census is performed here.

