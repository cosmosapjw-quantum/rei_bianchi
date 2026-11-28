# R10E literature notes: Magnus convergence and independent auditing

SciSpace was queried for convergence/error estimation of Magnus-type integrators for
time-dependent Schrödinger equations.

1. Hochbruck & Lubich, SIAM J. Numer. Anal. 41 (2003),
   DOI 10.1137/S0036142902403875.
   Establishes optimal-order error bounds for Magnus integrators applied to
   time-dependent Schrödinger equations and explains why they can perform well
   at larger steps than standard explicit methods.

2. Auzinger, Hofstätter, Koch, Quell & Thalhammer, ESAIM: M2AN 53 (2019),
   DOI 10.1051/M2AN/2018050.
   Constructs defect-based a posteriori error estimators for high-order Magnus-type
   integrators with time-dependent skew-Hermitian matrices and adaptive step selection.
   This supports future adaptive optimization, but R10E does not change integrator type.

3. Blanes, Casas, González & Thalhammer, IMA J. Numer. Anal. (2021),
   DOI 10.1093/IMANUM/DRZ058.
   Gives convergence/stability analysis for high-order commutator-free quasi-Magnus
   exponential integrators for nonautonomous Schrödinger equations.

4. Leimkuhler, Phil. Trans. R. Soc. A 357 (1999),
   DOI 10.1098/RSTA.1999.0366.
   Discusses adaptive regularization for perturbed Kepler/classical atomic trajectories.
   Relevant as a future optimization route for close Coulomb encounters, not as a
   requirement for the present fixed-step adapter.

SciSpace add-column returned no methodology/conclusion expansions for the selected
Magnus papers, so the synthesis above is limited to indexed abstracts/metadata.

R10E uses these references only to justify the architecture:
- retain the structure-preserving Magnus integrator;
- increase the fixed resolution under a new contract rather than retroactively
  weakening the 1e-7 gate;
- use a high-order adaptive Runge-Kutta solver only as an independent research auditor,
  not as the production propagator.
