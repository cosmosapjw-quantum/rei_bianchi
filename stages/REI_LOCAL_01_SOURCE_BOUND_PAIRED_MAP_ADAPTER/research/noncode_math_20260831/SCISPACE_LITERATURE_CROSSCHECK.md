# SciSpace literature cross-check — rei_bianchi non-coding derivations

**Date:** 2026-08-31 (KST)

The literature search was used as an external regression layer, not as a substitute for the repository-specific derivation.

| Topic | Primary/technical source | What it supports | What it does not supply |
|---|---|---|---|
| MPRK order, positivity, conservation | S. Kopecz & A. Meister, *On Order Conditions for Modified Patankar–Runge–Kutta Schemes*, arXiv:1702.04589 (2017) | MPRK construction, unconditional positivity/conservation, first/second-order conditions | the rei_bianchi four-site H/He–thermal map or its shared-dependency remainder |
| Validated explicit/implicit RK | J. A. Dit Sandretto & A. Chapoutot, *Validated Explicit and Implicit Runge–Kutta Methods*, HAL-01243053 (2016) | interval contractors and validated local truncation-error methodology for RK methods | the project-specific Patankar/OTS/owner algebra |
| Taylor models + validated path tracking | A. Guillemot & P. Lairez, *Validated Numerics for Algebraic Path Tracking*, arXiv:2401.17973 (2024) | Taylor-model/interval predictor-corrector certification and dependency-aware nonlinear tracking | a ready-made full-versus-two-half certificate for this solver |
| IGM thermochemistry fits | L. Hui & N. Y. Gnedin, *Equation of State of the Photoionized Intergalactic Medium*, arXiv:astro-ph/9612232 | temperature-dependent recombination/cooling fitting structures and thermodynamic context | the exact OTS branch ownership and state-dependent photoheat derivative used here |
| H/He C2-Ray rate authority | M. M. Friedrich et al., *Radiative Transfer of Energetic Photons: X-rays and Helium Ionization in C2-Ray*, MNRAS 421, 2232 (2012), Appendix G | the H/He recombination, collisional ionization, and cooling rate family used by the project | the dependency-preserving MPRK22–SDIRK2 paired-map proof |
| Non-equilibrium ionization-front thermal coupling | C. Zeng & C. M. Hirata, *Non-equilibrium Temperature Evolution of Ionization Fronts during the Epoch of Reionization*, arXiv:2007.02940 | physical importance of coupled species/energy evolution and implicit treatment of stiff thermal exchange | the current code’s interval/Krawczyk/Taylor certificate |

**Literature verdict:** the selected numerical and microphysical ingredients are defensible, but the decisive blocker is genuinely project-specific. No cited paper removes the need to derive and certify the same-parent source-bound difference map
\(\Phi_{h/2}\circ\Phi_{h/2}-\Phi_h\) with all implicit, source-site, event, and ledger dependencies retained.
