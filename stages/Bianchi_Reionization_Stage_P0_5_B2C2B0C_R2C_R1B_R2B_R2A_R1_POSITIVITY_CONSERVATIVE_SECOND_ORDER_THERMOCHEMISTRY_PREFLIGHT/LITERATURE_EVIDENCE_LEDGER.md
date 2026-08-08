# Literature evidence ledger

- Kopecz & Meister, *On order conditions for modified Patankar--Runge--Kutta
  schemes*, Applied Numerical Mathematics 123 (2018), establishes first- and
  second-order conditions for positivity/conservation-preserving MPRK families.
- González-Avila et al., *Extension of modified Patankar--Runge--Kutta schemes
  to nonautonomous production--destruction systems*, JCAM 389 (2021), treats
  second-order nonautonomous extensions while retaining positivity and mass
  conservation.
- R. Alexander, *Diagonally Implicit Runge--Kutta Methods for Stiff O.D.E.'s*,
  SIAM J. Numer. Anal. 14 (1977), derives the two-stage order-2 strongly
  S-stable DIRK family used for the thermal attempt.
- Friedrich et al. (2012) extend C2-Ray to H/He multifrequency transport and
  show that temperature accuracy can impose stricter timestep requirements than
  ionization fractions.
- PETSc `TSSetPostStep` and event APIs call commit-like callbacks only after a
  successful step and distinguish rollback/event handling, matching the
  project's transactional accepted-history policy.
