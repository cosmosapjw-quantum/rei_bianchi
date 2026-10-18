# R9 Unit4 NCP scientific review — 2026-10-16

**Decision: PARTIAL_WALL_LIMIT.** Independent read-only review accepts the repaired Hamiltonian reconstruction and finite diagnostics at Krylov lengths 16, 32, and 64. The declared spectrum/CDF refinement is **HOLD**. This is not a physical no-go.

The first run failed the compressed anti-Hermitian gate at length 16 (9.156432964e-9 versus 4.892643267e-9) after 19 H-actions. A zero-H-action diagnostic found packed ERI pair-exchange asymmetry of 1.876626342e-6. One reviewed targeted repair symmetrized real h and packed ERI before the unchanged frozen V6 raw_action. It retained every reconstruction, Lanczos, and refinement tolerance. Eleven targeted tests passed on the NCP PySCF environment. Actual reconstruction then passed all nine gates; the ground residual was 3.192032266e-8 Eh.

The repaired milestones passed every internal gate. At 64, Gram error was 9.105223e-14, ground leakage 4.144270e-16, and anti-Hermitian error 1.990623e-13. Direct and quadrature moments agreed to their declared tolerances. The conditional mean was 2.6682103412278595 Eh and variance 17.09645547454128 Eh². The six largest-weight Ritz residuals span 1.55e-7 to about 0.481 Eh, so the individual poles are finite Ritz diagnostics.

The 32→64 refinement failed for η=0.05, 0.1, and 0.2 Eh. At η=0.05, spectrum L1/W=0.407978, maximum CDF change/W=0.0410945, and window-mass change/W=0.00159157, versus 0.001 for each criterion. The other η values are in the raw milestone JSON. The 64-point raw quadrature weight above 20 Eh is 0.004600803179358788 and below 0 is zero. Analytic Lorentzian tails are different quantities and are retained without window renormalization.

The same bounded worker attempted 128 but the original absolute deadline terminated it before a 128 milestone. The terminal receipt is `partial / wall_limit`, with the 64 checkpoint preserved. Final H-action count is UNKNOWN because the supervisor killed the worker before its receipt; the checkpoint certifies 86 cumulative actions and the enforced cap was 160. The two supervised executions total 6814.655513 s. Repaired sampled peak RSS was 1.105045 GiB. The terminal receipt timestamp is 46.897 ms after the absolute deadline, consistent with the 50 ms supervisor polling interval.

The saved complement includes bound excited states. W is not an ionization probability. This finite Ritz spectrum is not an energy-normalized physical continuum distribution. Electron capture, continuum channels, complete-basis closure and associated physical admission remain separate dependencies. No further run or repair was authorized after this expired budget.

Review authority: independent read-only `costroute-research-review` role (requested Astra/xhigh profile); actual runtime identity was not independently observed. The reviewer rederived C/J, mass/moments, Lorentzian spectrum/CDF, refinement and terminal classification from raw evidence.
