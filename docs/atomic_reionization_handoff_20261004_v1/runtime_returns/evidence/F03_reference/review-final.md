1. **P2: zero-rate helium state rejects instead of remaining unchanged.** In [microstep.rs:182](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/microstep.rs:182), subtraction reconstructs a negative `p1` from roundoff.
   - Input: fixture model with `sigma`, `alpha`, `beta` all zero; fixture state with `fractions=[0.01,0.0,0.1]`; `dt=1e9`, default control.
   - Direct observation: RHS is exactly zero, but `implicit_hhe_step` returns `HHE_STATE_DOMAIN`. `try_hhe_step` correctly preserves its caller state.
   - Scoped fix: compute the helium numerator from nonnegative production terms using the stored initial HeII fraction, avoiding subtraction from unity.

2. **P2: a valid helium boundary returns negative event rates.** [hhe_events.rs:203](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/hhe_events.rs:203) and line 237 evaluate `1-he1-he2`, while validation uses `he1+he2`.
   - Input: default fixture model/state, replacing fractions with `[0.01,0.9,0.1]`.
   - Direct observation: sum is `1.0`; `hhe_rhs` succeeds with HeI photo rates `[−0.0,−9.668900019410563e−35,−1.3812714313443663e−36]` and collision rate `−2.333661042186464e−44`.
   - These are roundoff-scale, but violate nonnegative event ownership. Use one consistent neutral-fraction expression, `1-(he1+he2)`, across validation, RHS and iteration.

3. **P2: temperature silently accepts intermediate overflow.** [hhe_events.rs:145](/home/cosmosapjw/Dropbox/bianchi/rei_bianchi/rust/rei_microphysics/src/hhe_events.rs:145) checks only the final quotient.
   - Input: default model with `n_h_cm3=1e308`, `n_he_cm3=0`; state `fractions=[1,0,0]`, `u_erg_cm3=1e300`, photons and escape zero.
   - Direct observation: `temperature()` returns `Ok(0.0)` because particle-density addition overflows. A scaled evaluation gives approximately `2.4143235053466402e7 K`.
   - This concerns the explicitly requested finite-input/overflow boundary, not the nominal fixture. Reject nonfinite intermediates or use overflow-safe evaluation.

Direct Rust reproductions and observed output: [probe.rs](/tmp/rei-f03-review-be8g_3gm/probe.rs), [probe.log](/tmp/rei-f03-review-be8g_3gm/probe.log). Compiled the exact candidate into `/tmp` and executed through `cuhg-telemetry` under `REI-F03`.

All seven candidate hashes and the original fixture hash matched. Nominal validation/convergence results were **inspected receipts**, not rerun. Registration records `gpt-6-astra/xhigh`, fresh context, launch `cl_b27b7a437f202b97443619c92c383f20`; runtime identity adjudication remains with the parent.

Single review complete; three scoped findings require correction. No repository edits or scientific admission.
