# V13 C8: actual sandbox native source-on experiments

New V12 backup was the starting point, not an assumed unrun V12. Parent PR195 source commit 46b567e0ee96e725a21e77fed9ab4160d0ffa9e7. Original production and other branches/checkpoints untouched.

## Executed
Rust 1.94.1 in ChatGPT sandbox. 29 targeted tests PASS (7 new), source-on native sweep binary built. Broad crate regression: 334 passed, 16 failed because the V12 capsule lacks BASS CSV/JSON and signed-continuation fixtures; failed targets axbi_bass_dynamic, axbi_bass_passive, axbi_signed_resource_continuation. Do not report whole-repository PASS.

119 actual source-on/control histories, 8792 step rows, seven opt-in modes. Three sets: Xend=1e-5/cells8/tol1e-13/Nmax128, Xend=1e-5/cells8/tol1e-15/Nmax256, Xend=1e-4/cells32/tol1e-15/Nmax256. Original initial gas .075/.12/.03, T15000K, a0=1/21, total-H normalization and source fesc=.2.

At the last N64/128/256 triple, tight short case photon self-order improves BE .98210 to combined 1.98278. Temperature BE .99859 versus combined .16662 with a sign change. Long case photon order BE .52205 to combined 1.86557; combined temperature 3.17412 has cancellation and is NOT a third-order or global second-order claim. Long source-off temperature control p=2.01284. Maximum recorded energy residual 4.573674772245795e-12 eV/H; photon residual 7.623296525288703e-21/H. Sum of history wall timers 5.269816618 s is this sandbox only, excludes builds.

Source halves at common midpoint geometry are not retarded GL2 source-age integration. Exponential attenuation with matched interval-mean photon occupation is positive at fixed nonnegative opacity, not an unconditional gas positivity/stiff-accuracy guarantee. Species photo events and photon heat/binding share one owner; nonphysical gas/root failure rejects transaction. Experimental controls are fresh fixed-run only, not serialized into restart checkpoints.

No independent source-on continuous RHS was run; all source-on global order, full EoR, Case B and signed Bianchi remain HOLD. Native subagent review unavailable, NOT_RUN. Raw 119-run CSVs, analysis and all test/failure logs are in C8_CHECKPOINT.tar.gz (Drive id 12803zJp1Fb7Ckj3sPycQpiwfc1x3wp82) and final full archive. C8 stage Drive/Library uploads acknowledged; final archive whole-byte readback is recorded separately.

The complete RUN_V13.sh was independently restored/built and executed in a new sandbox directory: 29 tests plus two time intervals, 28 smoke histories/336 rows, exit0. Smoke is separate from 119 scientific histories. NCP can run this published script with no solver implementation work.
