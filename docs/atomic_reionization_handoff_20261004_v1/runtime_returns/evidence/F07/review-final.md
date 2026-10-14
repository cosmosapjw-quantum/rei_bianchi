1. **MAJOR — The frozen scenario conflates binding energies with actual Verner cutoffs.** [Config line 29](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/configs/rei_fastest_v1/science_scenario_v1.json:29) declares `[13.5984346,24.587389,54.41776]` as provider thresholds and requires common chemistry/support/thermal thresholds. The existing [provider](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/atomic_provider.rs:335) instead cuts off at `[13.60,24.59,54.42]`; FT03 separately uses binding energies. Directly compiled production code returns `sigma_HI(13.599)=0` and `sigma_HI(13.60)=6.346296358990503e-18`. For FLRW, the actual absorption cutoff crossing is `7.326040092073e11 s`, versus the screening’s binding crossing `7.441149658101e11 s`—a 1.55% distinction. **Smallest repair:** preserve both authorities explicitly, distinguish their crossing diagnostics, and include the actual active cross-section discontinuity in support handling. Do not change the frozen provider.

2. **MAJOR — Temperature screening trusts a configurable implementation domain.** [Validator line 74](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/docs/atomic_reionization_handoff_20261004_v1/tools/verify_science_scenario.py:74) checks only relative nesting. A temporary candidate declaring implementation guard `[1000,200000]`, scenario guard `[1000,160000]`, and initial `120000 K` receives `PASS`; the directly compiled FT03 API rejects that temperature with `FT03_TEMPERATURE_DOMAIN`. **Smallest repair:** bind the implementation guard to the actual `[30000,110000] K` API domain before checking scenario nesting.

3. **MINOR — Positive angular quadrature is not validated.** [Schema line 545](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/configs/rei_fastest_v1/science_scenario_v1.schema.json:545) accepts arbitrary finite numeric counts, and screening never checks them. Changing only `n_mu` to `[0,8,16]` receives `PASS`, although `Delta_mu=2/n_mu` is undefined. **Smallest repair:** require positive integer counts and verify the declared weights are positive and normalized.

4. **MINOR — Screening can certify negative thermal energy.** Changing only `k_B_erg_K` to `-1.380649e-16` receives `PASS` and reports `initial_thermal_erg_cm3=-2.182288325625E-15`. **Smallest repair:** check the declared physical constants against their fixed positive values and reject invalid derived initial energy.

Findings 2–4 are validator acceptance gaps; the unmodified candidate’s corresponding values are valid.

Executed evidence is preserved in [probe.stdout](/tmp/rei-f07-review-01a107d4-0wrv8700/probe.stdout), with [probe.py](/tmp/rei-f07-review-01a107d4-0wrv8700/probe.py), argv files, individual mutated inputs/results, and the Rust provider probe beside it. The canonical validator exited 0 and reproduced the frozen screening byte-for-byte. Independent arithmetic reproduced EOS, source normalization, geometry bounds, and positive normalized weights for all three declared angular grids. All six candidate hashes remained unchanged.

Source inspection confirms both photon guard ledgers exist. The inherited four-group `cMpc^-3`, packet reference-`cm^-3`, and scenario per-H quantities require explicit conversion in the future adapter; that adapter is already declared unimplemented. No histories, complete legacy suites, invariant temperature proof, physical-error assessment, or scientific admission were performed. No repository files were changed. Host owns disposition.

<oai-mem-citation>
<citation_entries>
MEMORY.md:3360-3361|note=[Applied trusted local scientific review scope]
</citation_entries>
<rollout_ids>
</rollout_ids>
</oai-mem-citation>
