# Nonlinear residual and adaptive-error diagnostic budget

## R1 — position and scope

This unit constructs a deterministic diagnostic that maps an actual four-component backward-Euler residual and Jacobian into the coordinate scaling used by the existing adaptive comparison. It reports a linearized Newton correction, conditioning and linear-system backward error. Missing stage residual/Jacobian data yields HOLD for actual-stage attribution. Production source005, the active source009 runner, their tolerances and their states are unchanged.

Read-only GitHub intake is pinned at `fdfda0fec423ccb7175552c7dc066be93ce347e1`; exact blob identities and inspected source excerpts are in `evidence/SOURCE_PIN.json` and `evidence/SOURCE_EXCERPTS.txt`. The current `ResidualContext.evaluate` orders unknowns as `(x_HII,x_HeII,x_HeIII,w_eV_per_H)` and evaluates `R=y-y_old-dt*f(y)`, with prepared absorption fixed throughout each chemical-stage Newton solve. The existing termination threshold is 1e-11 in its own residual scaling, and the adaptive target is 1e-5 in a different state scaling.

The source007 independent review observed larger temperature differences after refinement, accepted-stage maximum Newton residuals near 9e-17 for h/2 and 7.36e-12 or 9.05e-12 for h/4, and nonidentical actual endpoint bits. It identified nonlinear termination as a supported confounder, without proving its contribution. The saved maximum alone does not identify a residual vector, a Jacobian, a stage or a linearized state correction. The new diagnostic fills that explicit computation and input contract, with synthetic fixtures testing its mathematics independently of the active runner.

The existing full005 PL result at commit `0c3958d11d654513eb23cf462d5148e87ba6c9de` is reused: saved-PL Tgas supremum 0.24946455408644397 K and RMS 0.1128202745602529 K. Its postprocessing cumulative debit 156.5376037069618 s of 300 s and original deadline remain its own retained allocation. No PL check, solver campaign or full-data reduction is repeated here.

Completion requires a derived scale transformation, an explicit distinction between residual and state error, a backward-Euler full/half-step example, independent algebra/fixture checks, and a standard-library implementation contract accepting actual stage packets. This unit may create only new files under `research/flrw_nonlinear_error_budget_20261016/`; no production Rust or canonical campaign file is mutated. Actual-stage diagnosis remains NOT_RUN until a correctly identified packet is supplied by its owner.
