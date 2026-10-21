# Research state — age exposure / native BE lane

Updated 2026-10-21 from PR199 `dd24a9f89e847ae7e97c017ffededd4aa53790d8`.

- v10 optimized native BE time8, time16, time32 execution is complete and validated; do not repeat.
- Saved-output three-level diagnostic passed for 12 scalar endpoint components. Adjacent difference magnitudes decrease across these three stored native-BE cases; finite-grid slopes vary by observable.
- Original 0.005 acceptance remains unmet for both time8↔16 and time16↔32.
- Positive DOP853 age32 is a different operator and is not a fourth native-BE grid.
- `native_age_time_convergence=HOLD`; `nonlinear_Grackle_response_bound=NOT_ESTABLISHED`; `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
- No solver case, model, finite cap, or tolerance was changed or launched in this follow-up. One analysis script failure was preserved and one Astra-authorized index correction completed. Independent result review PASS permits factual diagnostic publication; cumulative 60s compliance is NOT_ESTABLISHED because attempt001 elapsed was not recorded.
- No new NCP execution is ready in this lane. The next work requires a new scientific question and Astra contract.
