# Method references

- Mellema, Iliev, Alvarez & Shapiro, *C2-Ray: A new method for
  photon-conserving transport of ionizing radiation*, New Astronomy 11
  (2006) 374–395, DOI `10.1016/j.newast.2005.09.004`, arXiv
  `astro-ph/0508416`. Used for the photon-conserving and analytic-relaxation
  audit principle.
- Friedrich, Mellema, Iliev & Shapiro, *Radiative transfer of energetic
  photons: X-rays and helium ionization in C2-Ray*, arXiv `1201.0602`.
  Used for the H/He multi-frequency timestep and temperature-sensitivity
  caution.
- PETSc TS 3.25 documentation, `https://petsc.org/release/manual/ts/` and
  `TSBEULER`. Used as the reference implicit ODE/DAE and backward-Euler
  formulation; PETSc is not invoked as a hidden solver in this stage.
- Benamou, Carlier, Cuturi, Nenna & Peyré, *Iterative Bregman Projections for
  Regularized Transportation Problems*, SIAM J. Sci. Comput. 37 (2015), DOI
  `10.1137/141000439`. Used for KL/Bregman projection on linear equality and
  capacity-inequality constraints.
- Birgin & Raydan, *Robust Stopping Criteria for Dykstra's Algorithm*, SIAM J.
  Sci. Comput. 26 (2005), DOI `10.1137/03060062X`. Used for stopping/gate
  interpretation of the constrained projection auditor.
