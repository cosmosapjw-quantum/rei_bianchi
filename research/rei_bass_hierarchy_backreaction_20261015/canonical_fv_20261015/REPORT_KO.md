# REI Sigma–pi_ab positive canonical momentum finite-volume Vlasov

Date: 2026-10-15 KST. Source parent REI PR140 SHA b1cba753083ad83049c23ff538834564b49b7b6e; original BASS PR160 sigma_matter.py SHA256 1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790. Current highest REC/REI source distinction: REI PR141 and PR142 have ALREADY performed limited native HHe-Einstein two-way coupling near z4, whereas full stellar-source momentum Q^a and cold z20→4 remain unresolved. This implementation is an alternative positive kinetic supplier, NOT a repeated claim to implement C15 HHe for the first time.

## New constructive physics

Metric signature (-,+,+,+), ds²=-c²dt²+a²[e^-2b (dx²+dy²)+e^4b dz²]; s=dot b, sigma^i_j=diag(-s,-s,2s), Sigma=sqrt(3)|s|/H and separate orientation sign(s). Historical signed q_ref is only a source-compatibility adapter.

Instead of using an exact high velocity-index J^(i) or l=4 moment as a source for a truncated time-evolving hierarchy, the new closure stores *nonnegative finite-volume cell populations* in the two conserved canonical momentum variables q and mu_ref. In spatially homogeneous collisionless Bianchi I, spatial Killing momenta q_i=a_i p_i are invariant. Hence each comoving canonical cell count satisfies dN_cell/dln(a)=0 EXACTLY, and physical momentum evolves by p_perp=q_perp exp(-eta+b), p_parallel=q_parallel exp(-eta-2b), eta=ln(a/a_ref). The moving physical velocity mesh is a Lagrangian method. Not an Eulerian flux scheme for collisions.

The source positive Fermi–Dirac distribution is proportional to q² fFD(q)[1+A_m P2(mu_ref)]dq dmu_ref/2, with -1<=A_m<=2, mass/T_ref in [3,1e5]. The radial interval q ∈ [0,infinity) is mapped to t=(q-3)/(q+3)∈[-1,1]. Each disjoint t,mu cell has positive Gauss2 or Gauss3 internal quadrature packets, initially normalized to its own exact discrete massive rho_ref. The original Omega_m is split into (1-f_m) dust plus f_m nonbaryonic massive kinetic energy, and f_m Omega_m<=Omega_m-Omega_b, so no double count. Original gamma and massless-nu species, Thomson gamma-only unpolarized E2=0 and external actual HHe electron n_e(a), are preserved from PR137. The momentum cells are NOT ionizing photons, baryonic gas viscosity, or observed neutrino mass.

For P_perp=(p_perp²/(2E)) packet integrated, P_parallel=(p_parallel²/E) packet integrated, rho=E packet integrated, define pbar=(2P_perp+P_parallel)/3 and DeltaP=P_parallel-P_perp=3 pi_s. The source identities, exact for the discrete collisionless ensemble, are partial_eta rho=-3(rho+pbar) and partial_b rho=-2 DeltaP. Thus d rho/deta=-3(rho+pbar)-2(s/H)DeltaP. Wolfram source shell identity returned exact {0,0,0}. The Einstein source uses pi_s=DeltaP/3 so its LRS shear equation retains the PR137 factor-of-three convention. Full momentum source positivity is preserved without projection.

## Actual source and numerical execution

Original BASS PR160 MassiveMoments evaluated from unchanged source at m/T_ref=3,30,300 with positive angular quadrupoles A=-0.7,0,+0.5 and multiple eta,b. A failing m/T=3 two-point subcell quadrature was repaired using third-order positive subcell integration, not loose tolerance. At 32×16 canonical cells, Gauss3 source errors reached about 2e-13 to 4e-13 for m/T=3 in the nontrivial eta=.8,b=-.017 case, versus original BASS GL96 source. All 18 new source tests PASS, including physical rho/p positivity and particle count, pressure cone, independent eta and b energy conservation, BASS original moment and PR140 Einstein comparisons, zero-fm exact PR137 reduction and Raychaudhuri identity.

8 actual zbar20→4 Einstein + positive canonical FV massive + source gamma/nu/Thomson runs, 121 snapshots each, total 968 states. Sigma_ref=0 with both gamma and massless-nu initial quadrupoles +0.2, massive fraction fm=.1 when present:
- no massive 0.00010149170072417655;
- mass30 A_m=+.5, +Thomson: 0.0001303240572010518;
- mass30 A_m=-.5: 0.00007273826829881095;
- mass3 A_m=+.5: 0.001559047351884471;
- mass300 A_m=+.5: 0.00010178381162663367;
- mass30 A_m=+.5 without Thomson: 0.0001309027031229716;
- signed Sigma_ref≈0.01731964, orientation+ and -: 0.0021108020861652483 and 0.0018500104314265633.
These are conditional BASS physical models, NOT measurements, neutrino mass fits or HHe gas temperature changes.

The independent original active PR140 J^(i) Einstein hierarchy, not supplied as trajectory initial data, differed in final Sigma across all eight by no more than 2.2896279056744406e-12. Three actual cases of combined nominal 24×12 Gaussian3 cells, photon L8 vs refined 48×24 Gaussian3 cells, photon L12 and tighter time tolerances: final |Delta Sigma| = 1.15777e-13 (warm mass3), 3.50132e-13 (mass30) and 6.02525e-13 (signed). Original PR140 in these 3 cases agreed to <=5.09319e-13. Full source-specific+inherited regression 50 PASS. Source C2 electron interpolation original history SHA256 4f6852c3a5152b91224ce5fecad6ccdfe9f7ece4c8a6d39825c6f5e5ca8ae92f and maximum source n_e interpolation relative deviation 1.9755e-4, separate from much smaller numerical error.

## Performance, source authority and claim

1536 matched scalar vs chunked positive cell source evaluations (24×12 cells, order3) gave 2.4768737879609035× NumPy batch acceleration at checked float64 parity, not full native REI production speedup. Eight independent Einstein source cases: two-process 1.6197565478778233×, four-process 1.9925672920583353× versus local serial under same source inputs and numerical outputs.

Source code canonical_fv.py, run_canonical_fv.py, verify_fv_and_plot.py, tests, three science plots, 968-row CSV, machine-readable RESULTS.json and CONVERGENCE.json. Original dirty production REI worktree/checkpoints untouched. No local Codex, native subagents NOT_RUN because unavailable.

SCOPED_PASS: conservative collisionless finite-canonical-cell model, source-coupled Einstein and original BASS/PR137 radiation+massive physical reference and numerical convergence. NOT_ADMITTED: conservative Eulerian collision finite-volume flux, massive elastic scattering, E/B polarized Thomson, source-gravitating stellar reservoir and escaped photons Q_r^a closure, fully reactive HHe feedback under changed FV metric, complete cold z20→4 native AX08 or observational inference.

Next constructive selected coding task: source-owned positive collision redistribution between canonical momentum cells preserving number and 4-momentum *with actual gas recoil*; meanwhile the existing limited C15 H/He coupling from PR141/142 should be reused as a separate, source-preserved branch rather than duplicated.

Literature basis: spatially homogeneous Einstein–Vlasov Bianchi I dynamics, https://doi.org/10.1088/0264-9381/23/10/016; conservative Vlasov advection source, https://people.rennes.inria.fr/Nicolas.Crouseilles/cms.pdf. Numerical source authority is the exact BASS PR160 source and original PR140 and PR137 programs.
