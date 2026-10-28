# PREEXEC_PASS — R1 and R2 closed

Independent changed-line review,2026-10-25. This supplements PREEXEC_REVIEW.md; it does not rerun the completed static theory review.

R1: observed negative-control isotope and charge residuals are computed from each mutated reaction and saved separately from literal expectations. Separate exact-residual comparison rows retain expected independence. Closed.

R2: root authorized the additive photon-count clarification. Actual changed source and fixture lines were inspected. Case01 supplies photon_count_per_event−1 and independently15eV; case02 supplies+1 and15eV. Each expected photon dictionary literally contains count, energy, signed increment and zero residual. radiation_event computes count×energy and compares against the independently supplied radiation reservoir increment. radiation_source applies the exact normalized rate, permits signed tangents only through the declared flag, and preserves event count separately from material isotope/charge rows. Reversal negates count and reservoir increment while retaining photon energy. All other cases remain UNQUALIFIED with None values, without implicit zero. Source/JVP/reverse comparisons use literal expected input data. Closed.

Original immutable documents match between authority and staged copies:

- FROZEN_COMPILER_CONTRACT.md SHA256098b807f972f807b08fa3860635d5b03a5cedd9e91487743453b9a9ee4f9d9ef.
- THEORY.md SHA256ae1d5e5669c465d1548d4edc079991b28bff393613224e1c4b065560bc77a0e8.

The separate R2_PHOTON_COUNT_CLARIFICATION.md records the additive root instruction. No other scientific input, tolerance, budget, fixture domain or physical claim changed. This review performed reads and byte-identity checks only; no compiler import, fixture/test execution, solver or HD-adapter run.

Verdict PREEXEC_PASS. No unresolved static findings in this bounded unit. Positive transition: root S0 preservation → root-authorized single child within the existing cumulative30CPU/120wall/512MiB cap → one saved-data plot → final independent raw/resource/visual review. C9 scientific admission is still pending; this preexecution decision does not assert successful implementation, physical rate coverage, global completion or L4 readiness.

Final reviewed source/fixture SHA256 identities, relative to release/research/rei_chem_ledger_20261025:

| File | SHA256 |
|---|---|
| chem_ledger.py | 60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af |
| run_checks.py | 416b18e74a4c6e735c0ac14dbc6a6ccc55354f56b4fd429f8547c448cf089f15 |
| fixtures.json | bf0c2e7dbe0bccbafb00bc4874f9c1d439210b450d125701def1c881af9e4ae4 |
| run_bounded.py | 6fd4a37698a7bc7ed3f09fe7af3ce9cf9c4b63d91bd90ecba87ee9f933acb156 |
| plot_saved.py | c7b9e50ab6f95557e965b2cbfaeb7f188f09641775d5244a5ca13df63889dc29 |
