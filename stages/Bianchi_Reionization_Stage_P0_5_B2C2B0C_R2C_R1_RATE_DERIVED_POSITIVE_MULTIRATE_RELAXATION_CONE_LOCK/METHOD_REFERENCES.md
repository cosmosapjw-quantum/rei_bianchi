# Method references used for the R2C-R1 design

1. G. Mellema, I. T. Iliev, M. A. Alvarez, and P. R. Shapiro,
   “C2-Ray: A new method for photon-conserving transport of ionizing
   radiation,” arXiv:astro-ph/0508416. Relevant here: photon conservation and
   analytic local relaxation over a timestep.
2. M. M. Friedrich, G. Mellema, I. T. Iliev, and P. R. Shapiro,
   “Radiative transfer of energetic photons: X-rays and helium ionization in
   C2-Ray,” arXiv:1201.0602. Relevant here: coupled H/He multigroup physics and
   the stricter temperature timestep requirement.
3. L. Fainshil and M. Margaliot, “A Maximum Principle for the Stability
   Analysis of Positive Bilinear Control Systems with Applications to Positive
   Linear Switched Systems,” SIAM J. Control Optim. 50 (2012), 2193–2215,
   DOI 10.1137/11083808X. Relevant to the later Metzler-generator option.
4. SciPy documentation for `scipy.optimize.linprog(method="highs")`.
   Relevant here: HiGHS marginals use a sign convention opposite to many
   nonlinear-solver Lagrange multipliers.
5. M. Berz and G. Hoffstätter, “Computation and application of Taylor
   polynomials with interval remainder bounds,” Reliable Computing 4 (1998),
   83–97. Relevant here: centered Taylor enclosures with rigorous remainder
   bounds.

These references justify numerical and structural choices. They do not supply
any project-specific pass/fail result; those are derived from the locked local
artifacts and certificates.
