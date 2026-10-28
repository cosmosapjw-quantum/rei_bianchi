# Three-case prescribed-bath IVP proposal — NOT AUTHORIZED, NOT RUN

This proposal requests only an explicit exception to the existing main `NO_MORE_IVPs` restriction for the three named cases below. The already approved non-IVP cumulative planning30/presentation65 ceilings remain separate. Root confirmed the scoped implementation/review assessment; this remains a proposal awaiting the explicit exception and cloud-host permission.

| Case | External source | rtol | scaled atol |
|---|---|---:|---:|
| OFF_base | OFF; intrinsic decay/capture retained; external escape off | 1e-7 | 1e-11 |
| ON_base | Frozen alpha1 external forcing | 1e-7 | 1e-11 |
| ON_refined | Identical ON forcing | 2e-8 | 2e-12 |

Initial visible17 stocks are the first saved baseline row; fast Bn/BT and Un/UT begin at0. Hidden Li6 remains the prescribed saved bath. Time is elapsed proper seconds on the matched saved H background: t0=0 to t_end=9.742841241346858e16, corresponding to eta0→ln7 and mean-scale-factor z20→2. This is not absolute universe age. The exact output grid is the union of the201 reconstructed saved proper times and, for each frozen loss λn,λT,ksn+ken+λn,ksT+keT+λT,40 logarithmic points from0.001/loss to30/loss lying below t_end; duplicates are removed. It captures initial relaxation without a parameter sweep.

The prepared solver is Radau with the code's sparse dependency mask, scaled variables and augmented balance states. Commands, from the repository root, are:

```bash
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case OFF_base --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case ON_base --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
python research/rei_source_history_20261028/implementation/bounded_case_runner.py --case ON_refined --user-override-receipt research/rei_source_history_20261028/OWNER_IVP_OVERRIDE.json
timeout --signal=TERM --kill-after=1s 30s prlimit --cpu=3:3 --as=3221225472:3221225472 -- python research/rei_source_history_20261028/implementation/postprocess_cases.py
```

Run cases sequentially, worker1,3GiB, no automatic retries. Future execution must wrap each command with child/observer CPU measurement, immutable input identities and raw stdout/stderr/exit receipts. At most90 childCPU s plus10 observer/tailCPU s gives total new main reservation≤100. Inherited main595.225063 therefore gives cumulative maximum695.225063 under proposed temporary main cap700. Relative to original600 the cap increase is100/600=16.6667%, below the existing automatic budget threshold50%. Restore original main policy cap600 afterward, retaining cumulative debit; no balance reset or transfer. These are proposed limits, not measured runtime or an active allowance.

Stop on any failed case or exhausted bound and preserve raw outcomes; no blind retry. Acceptance is exactly the frozen contract: finite stocks; no stock below−1e-9 of its scale without a diagnosed failure; ON base/refined isotope-normalized difference≤1e-5 including transients; augmented baryon/charge residual≤1e-8 of the declared stock/throughput reference; exact event A/q tests; separate new-source energy identity and explicit old-bath reservoir ownership. Do not silently clip negative solver states or claim self-consistent photon/temperature evolution. A failed numerical criterion does not establish physical impossibility.

Budget permission alone does not remove the restriction. Historical `BUDGET_POLICY.json` has `"main_status": "NO_MORE_IVPs"`; AGENTS.md states: “This does not change scientific claim gates, reserved producer ownership, the existing NO_MORE_IVPs instruction, or the heavy-execution location policy.” The original first declaration/issuer is unknown. The permission sought is specifically a three-case exception to that existing restriction, followed by the frozen scientific acceptance review.

The root creates OWNER_IVP_OVERRIDE.json only after the actual explicit exception; no such receipt exists now. The prepared wrapper records one attempt per case, enforces fixed order and stops on a failed predecessor. Postprocessing has its own future presentation child≤3CPU s/wall30s/reservation3.5 under the continuing65 ceiling. Current closeout57.912723494 plus proposed3.5 is61.412723494; no present postprocess allocation or execution is claimed. The postprocessor uses the initial-particle-stock denominator, which is a stricter sufficient balance test than the frozen max(stock,absolute throughput) denominator. It does not measure or infer absolute boundary throughput from signed net ledgers.

Execution location proposed: this cloud bounded-pilot environment. The specific owner permission must cover these three cases on this host as a narrow exception to NO_MORE_IVPs and the preserved heavy-execution-location policy. No broader relocation or execution is authorized.
