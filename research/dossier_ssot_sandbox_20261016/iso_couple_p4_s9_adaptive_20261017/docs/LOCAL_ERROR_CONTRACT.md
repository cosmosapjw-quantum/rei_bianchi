# Conditional error model and actual admission

Signature(-,+,+,+). Proper t[s],species proper m^-3,photon count reference-comoving m^-3,thermal energy J/m^3,photon energy J/comoving m^3. c,k_B,EV_J retained. Background and atomic providers unchanged.

For a smooth order-p map with exact inner solves, coarse e_c=C h^(p+1),two-half e_f=2^-p C h^(p+1), so (e_c-e_f)/(2^p-1)=e_f. Wolfram algebra residual was0. In practice the defect has eta_c-eta_f from internal CX solves and other discretization errors. Common-mode inner error can cancel in step doubling. The test uses raw differences, not /3, because uniform p=2 across all observables was not established. This choice does not convert the indicator into an upper-bound theorem.

Atol vector: nuclei13x1e-10m^-3;thermal/escape/CMB1e-25Jm^-3;photon/group/sourcecount1e-22com^-3;photon/sourceenergy1e-37Jcom^-3;photoHI/HeI/HeII/DI[1e-22,1e-23,1e-28,1e-25]com^-3;P2energy ratio1e-12dimensionless. These are experimental local tolerances, not observation/EoR acceptance. Rtol scan is recorded separately. Norm=max of component ratios, not a norm on full source-age distribution.

Each fine photo-event density is multiplied by its own midpoint volume before two-step summation. Accepted endpoint contains only the second fine AgeHistory. No state/budget extrapolation or cohort pruning. Source/physics-ledger/inner-work errors are fatal; recoverable negative/temperature-domain trial states lead to a bounded h reduction. No clipping or tolerance loosening.

The next h uses .8*d^(-1/3) clipped [.2,2];rejections cap growth at.5. The exponent is a smooth-regime heuristic, not validation of global order. Termination,attempt,cohort and wall bounds live in the executable driver. Traces are flushed per attempt but are diagnostic logs, not full serialized restart states.

Lee,Mellema,Lundqvist arXiv1511.01040 DOI10.1093/mnras/stv2556 supports photo-heating-specific timestep motivation; SUNDIALS7.5 CVODE guide §3.4.3.2–3 motivates componentwise absolute/relative scales. Neither source validates our new implementation. SciSpace index dates/authors were cross-checked against primary arXiv metadata. New numerical evidence is independently traced to the supplied FULL ZIP.
