# HE18 / rei_bianchi directional Thomson-depth bridge (2026-10-15 KST)

**Authority:** downstream, source-scoped cold AXBI postprocessing. No replacement of BASS_HE warm HE18 P01 16-cell science/IVP certificate or its atomic microphysics.

## Exact source revision and verified scientific artifacts
- rei_bianchi independent research branch: research/bass-he-optical-depth-transfer-20261015, commit **334a4521243372558cbe1ec060cd954355d9b62e**.
- Exact deliverables: research/bass_he16_transfer_20261015/directional_tau_20261015/{directional_tau.py,DIRECTIONAL_TAU.json,DIRECTIONAL_TAU_RESULTS.svg,DIRECTIONAL_LINEAR_CHECK.json,DIRECTIONAL_FROZEN_GEOMETRY.json,DIRECTIONAL_PERFORMANCE.json,README.md}.
- Original five signed *cold* source histories: 200001 rows each, same source identity d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185, from q=0,+/-0.005,+/-0.01. Geometry b(a) caches have pinned parent source SHA manifests. No native solver was rerun or edited.
- Warm BASS_HE HE18 P01 FT03/HM12 source 16-cell original archive SHA256 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d. Different H/He abundance, temperature, photon stock, source closure and epoch; do not transplant numerical tau.

## Direct theory result
Original cold AXBI metric (-,+,+,+): ds^2=-c^2 dt^2+a^2 exp(-2b)(dx^2+dy^2)+a^2 exp(4b)dz^2. Normal photon sky cosine mu_o measured at observer time t_o.
Direction-dependent redshift from conserved comoving covector: (1+z_dir)=(a_o/a)*sqrt[(1-mu_o^2)*exp(2(b-b_o)) + mu_o^2*exp(-4(b-b_o))]. At fixed z_dir the emission proper time is mu-dependent, although Thomson d tau= sigma_T*c*n_e(t)dt is scalar at fixed proper endpoints for normal-comoving electrons.
At mean-emission a_bar=a_o/(1+zdir), leading directional optical-depth Legendre quadrupole coefficient a2_tau = 2*(sigma_T c ne/H)_at_a_bar * (b_e-b_o) + O(q^2). Observer is at the end of the shared *high-redshift prefix*: mean zbar_o approximately 10.2693, NOT our present z=0.

## Numerical results, signed prefixes
At zdir relative to that observer of 0.20, 0.50, 0.75:
- ZERO sky mean tau0 = 0.00173870684549, 0.00278345855850, 0.00304695696467.
- Even sky mean tau0 response ratio E(+/-0.01)/E(+/-0.005) = 3.99993011, 3.99997185, 4.00003761, consistent with q^2 leading.
- Odd sky optical-depth quadrupole ratio O_a2(0.01)/O_a2(0.005) = 1.99996126, 1.99982021, 1.99908465, consistent with linear q leading.
- At zdir=.5: E_tau0(.005)=-2.49195558e-8; O_tau2(.005)=-6.03751093e-6; first-order analytic a2 discrepancy relative to full calculation at q=.005 is 2.75285e-5.
- Frozen ZERO gas/clock with signed b geometry reproduces full odd a2 to relative 8.37e-6 through 8.33e-5 across the studied q and relative redshifts. This is an explicitly NON-self-consistent counterfactual diagnostic, not a new coupled Einstein/chemistry solution.
- The tau2 defined here is an optical-depth Legendre coefficient, distinct from existing AX08 photon-energy J2 and CMB polarization.

## Verification and optimization
- Actual Ubuntu: existing 33 parent tests + 12 new directional analytic/geometric tests PASS (45 total), checked by separate test-discovery invocations.
- Independent Python math/bisect scalar redshift roots and NumPy vectorized 128-direction roots agree at stored precision; benchmark medians 0.0181989s vs 0.00236746s (7.687x vector speedup).
- 1/2/4-worker cached-five-case angular moments: median 0.241475s/0.209096s/0.210840s; for this small task two workers are best, not a Rust solver speedup.
- Angular n=64 vs 128 convergence about <=3e-15 absolute in tau2 for the original cases. Source-row decimation 2,4,8,16,32 is a postprocessing diagnostic, NOT global source IVP error enclosure.
- Double backup archives + Dropbox byte-matched: code archive SHA256 ba76924a56a257ccb76211d5c821b2275aaad5d0418013e00d9a6a1d1ed104da, geometry cache archive SHA256 48c292eb92773dd9f056c4d32777c9bdff9b5ddc684f77de8ed48754fb3ae99b.

**Admission:** DERIVED/NUMERICALLY_CHECKED/IMPLEMENTATION_VERIFIED in the narrow read-only postprocessor. Global native ODE error, photon collision evolution, CMB polarized transfer and full present-day tau are UNRESOLVED. No physical detection claim.

Primary geometry reference: Fleury, Pitrou & Uzan, Phys Rev D 91, 043511 (2015), https://doi.org/10.1103/PhysRevD.91.043511 . H/He chemistry reference: Friedrich et al., MNRAS 421 2232 (2012), https://academic.oup.com/mnras/article/421/3/2232/1077406 .