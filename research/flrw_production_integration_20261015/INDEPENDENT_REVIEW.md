# Independent scientific review — 2026-10-15

**PASS_SCOPED_CHANGED_SEAMS.** Publication is supported for the implemented local-clock/initial-condition integration and standalone D/H charge-exchange operator. This decision does not certify a complete FLRW production history.

Requested reviewer execution was `gpt-6-astra`, reasoning `high`; actual runtime model identity was not independently observed. The reviewer read repository policy, source/intake contracts, finished source/test diffs and raw worker outcomes. The reviewer changed no source or git state and ran no tests or numerical experiments. Only these two review reports were written. Exact reviewed file SHA256 values appear in the JSON companion; base is `0fcb2dddf5de6b583c2e00f150abff0b2afb6315`.

## Clock and fresh donor initial condition

`log1p((a1-a0)/a0)` retains the interval represented by actual binary64 endpoints. Positive GL8 weights and positive H preserve positive proper time. Zero intervals, q=0 shear and signed-q reflection are handled consistently. The root explicitly authorized native log-panel width .01 and cap65536; these differ from the supplier prototype. GL4/GL8 disagreement is correctly labelled a diagnostic, not a rigorous error bound. Accumulated geometry and physical rates are unchanged.

The driver passes the same local dt to source injection and chemistry and reuses deterministic geometry snapshots. Existing rate/thermal channels, strict local target, photon/event ownership, domain rejection and ledger thresholds are unchanged. No clipping or extrapolation was added.

`initial_x_hii` is finite and constrained to [0,1]; the baseline remains2e-4. Fresh donor xHII=0.000210349192936 and T=9.306042400380866 K retain recipient nH/fHe. The donor temperature is already Kelvin. Neutral-He projection and source/recipient normalization differences remain conditional. No old baseline checkpoint was silently resumed with new initial data.

Observed targeted results are8 background plus13 driver tests PASS. They cover adjacent-ULP/matter analytic time, smooth reference, signed/zero shear, EOS/charge inversion, a controlled accepted step, conservation and checkpoint continuity. The final fresh probe passes for both initial conditions, each with2 accepted steps,20 comparisons,60 tentative trials,18 rejections and444 RHS calls. Both finish at a=0.04761904765537807: only microscopic progress from z20. This establishes changed-seam execution and checkpoint consistency; it does not demonstrate full-history practicality or convergence. Source/probe identity readbacks match.

The late-time sample reports local dt=6700735.980051018 s versus cumulative subtraction6700672 s. GL4−GL8=0 is not an exactness certificate. Single-call timings are not a general speedup benchmark.

## Standalone D/H operator

For x=D+, the contract has F=f(x), K=−f′(x), and d²=K²−4(kf−kr)F. The normalized implementation is algebraically the contracted Riccati displacement Fθ/(1+Kθ/2), including d=0, zero flux and stiff limits. Proper-SI densities and coefficients are explicit. Savin Table-2 direction/coefficient transcription, the factor10⁻⁶ from cm³/s to m³/s and the domain2.7–200000 K agree with the source contract. The6%/4% Table-1 comparisons test fit accuracy, not full atomic uncertainty or cosmological error.

H/D totals, baryons and charge are conserved. CT changes neither electron count nor thermal particle count. The explicit defect gives opposite chemical and thermal energy deltas; a negative final thermal state is rejected transactionally. There is no default D abundance, implicit cutoff-as-defect, clipping, production activation or legacy-projection bypass.

Observed first-attempt targeted results are7/7 PASS. Independent mathematical controls include the saved Wolfram manufactured value, frozen semigroup, pure-forward second-order depletion, pure reverse, stiff limits, an electron-omission negative control, thermal rejection and no-D no-op. This supports an exact frozen-rate fixed-volume kinetic map with thermal bookkeeping. It is not an exact temperature-dependent coupled thermal/expansion solution or a full D history.

## Decision limits and next action

No actual defect was found in the implemented seams; no repair was authorized. The bounded review is closed. Existing upstream/source/full-history evidence was reused under its original conditions, without broad reruns.

Repeated fixed-energy photon projection and its false threshold events remain unresolved. There is no new z20→4 abundance/temperature/optical-depth history or global refinement result. The old baseline history remains conditional reused evidence. Full D history still requires explicit donor D/H and D photo/recombination/energy/coupling inputs. HH rates, CR/massive channels and complete Einstein closure are not supplied by this change.

The next executable action is scoped publication of this implementation and evidence, followed by the already identified covariant native photon transport seam. These adjacent requirements do not block publication of the reviewed units.
