# Source007 two-case finite component observations

Both runs exited0, using the repaired binary and runtime checkpoint compiled identity 7a085a77634c39e65cf39150532a43d288233a9349c77803475479866b0e8f3e. Actual launch HEAD3ac94bbef9cfbf5345bf832383b8ed8aa620128b is retained; root delivery rebase to 32039b4779e79bdba464bac749443a9917e9e2e3 changes no compiled source bytes.

Each case used121 source grid points, dln(a)=0.0001, four main fixed steps and two extra checkpoint-resume steps on one worker. Per case main RHS52 plus resumed extra RHS26 gives78 actual calls; the extra count is derived from saved midpoint and exact native restart parity. No adaptive probe, tests, build or full campaign ran.

| Case | Proper elapsed seconds | Tgas K | signed s/H | Photon residual | Energy residual | Restart abs |
|---|---:|---:|---:|---:|---:|---:|
| COLD_FLRW | 3.380792498e+12 | 8.69922201847 | 0 | 3.558e-20 | 4.337e-19 | 0.0 |
| SIGNED_MINUS | 3.380624043e+12 | 8.69919161606 | -0.00999346067321 | -1.016e-20 | -4.337e-19 | 0.0 |

Frozen acceptance observations are in RETURN_CONTRACT.json and raw case inspections, including source increment, Newton, Hamiltonian, native Raychaudhuri row checks and instantaneous energy ownership. Native point-minus-interval clock residual is zero in both runs. GL4/GL8 differences are not emitted by this example and remain null; zero clock consistency residual is not a numerical error bound.

Source007 baseline IC xHII2e-4 and T8.098143045064857K differs from source005 REC temperature9.306... . SIGNED_MINUS remains physically nonzero shear although analytic q_ref=0. Full convergence remains HOLD and scientific admission is NOT_ISSUED pending fresh independent review.

New component wall 0.130703988019377 seconds of120; prior three compile/test invocations and20.121775138075463 seconds remain recorded.
