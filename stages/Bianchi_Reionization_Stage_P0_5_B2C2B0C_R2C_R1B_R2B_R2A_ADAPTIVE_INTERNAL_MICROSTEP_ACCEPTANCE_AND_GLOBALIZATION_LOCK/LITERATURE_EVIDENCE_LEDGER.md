# Literature evidence ledger

## Load-bearing numerical/physical basis

- Mellema et al., *C2-Ray: A new method for photon-conserving transport of
  ionizing radiation*, arXiv:astro-ph/0508416. Supports owner-correct absorbed
  photon accounting and positive local chemistry; it does not supply this
  project's subgrid closure.
- Friedrich et al., *Radiative transfer of energetic photons: X-rays and helium
  ionization in C2-Ray*, arXiv:1201.0602. Supports independent thermal and
  ionization timestep gates in multifrequency H/He calculations.
- Kopecz and Meister, *On order conditions for modified
  Patankar–Runge–Kutta schemes*, Applied Numerical Mathematics 123 (2018),
  DOI 10.1016/j.apnum.2017.09.004. Establishes first- and second-order positive,
  conservative MPRK constructions for production–destruction systems.
- Izgin, Kopecz and Meister, *On Lyapunov stability of positive and conservative
  time integrators and application to second order MPRK schemes*, ESAIM M2AN 56
  (2022), DOI 10.1051/m2an/2022031. Supports the next-stage stability audit.
- *Extension of modified Patankar–Runge–Kutta schemes to nonautonomous
  production–destruction systems based on Oliver's approach*, JCAM 389 (2021),
  113350. Supports a nonautonomous second-order candidate for the next stage.

## Implementation and transaction basis

- PETSc TS documentation: implicit ODE/DAE residuals use `F(t,u,udot)=0`,
  nonlinear solves use SNES, adaptation accepts or rejects trial steps, and
  post-step callbacks occur only after successful steps. These semantics are
  referenced, not numerically imported.
- JAX asynchronous-dispatch and benchmarking documentation: timings require
  warm-up and synchronization such as `block_until_ready`; X64 must be enabled
  explicitly. The stage followed these rules and still found sequence-level
  synchronization instability.

## External project monitoring

`rec_bianchi` v0.63 is used only as a semantic compatibility reference for
transactional ownership, componentwise ledgers and fail-closed underidentified
couplings. Its directional state, COM network, preconditioner and recombination
history are not inputs to this stage.
