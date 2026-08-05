# Independent review and red-team decision

## Strengths

1. Rate bounds and mode count were frozen before feasibility.
2. No node-wise free fit, clipping, mass-from-opacity inversion, or
   inter-macro transport was used.
3. Every equilibrium failure has a compact Farkas certificate that can be
   replayed without the production solver.
4. Every equilibrium pass has an independent KKT certificate and an analytic
   trajectory certificate.
5. Failed numerical and semantic attempts are retained rather than rewritten.
6. The mode-count theorem sharply separates equilibrium no-go from
   interior-trajectory flexibility.

## Critical limitations

1. The no-go is conditional on macro-shared rates. The inherited state has
   local density, temperature, opacity, current, and transfer fields, so the
   physical local-rate alternative remains open.
2. `C` and `J_g` are interval nuisance families, not a closed microphysical
   evolution law. Their failures cannot yet be interpreted as a failure of
   reionization physics itself.
3. Only 27/43 analytic passes satisfy the deliberately strict coarse-refinement
   gate; however all 43 pass at four and eight steps, so this does not explain
   the 497 equilibrium failures.
4. Wolfram and the requested special-function plugin were unavailable. The
   exact fallback is strong, but a later environment should still execute the
   included `.wl` script and record the native transcript.

## Rejected conclusions

- “Two modes solve the history problem”: false; they solve only 42 interior
  path failures after equilibrium feasibility.
- “A smaller timestep solves the stage”: false; the dominant failure is an
  empty equilibrium box.
- “The rate bounds should be widened by the dual deficit”: circular and
  forbidden.
- “No physical history exists”: not established; node-local deterministic
  rate fields and coupled/non-autonomous operators remain untested.

## Recommended next decision

Test the smallest additional physical freedom first: node-local rate evidence
computed deterministically from inherited local fields, with at most a small
macro-shared hyperparameter set locked before feasibility. Only if that model
remains fail-closed should the project introduce a coupled positive generator
in the current/capacity and mass/headroom coordinates.
