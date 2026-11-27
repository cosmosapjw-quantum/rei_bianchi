# R10G source and calculation provenance

## Primary project sources

Repository: cosmosapjw-quantum/BASS_HE, immutable commit 5efe052460e85f7e9785b9391d188ba394efee73.

- research/shared_c64/20260930/CODE_I02_R10F_EXECUTION/20260930T1026KST/REPORT_KO.md
- same namespace FIXED_GK_DIAGNOSTIC.json, EXACT_NODE_TABLE_MANIFEST.json, BACKUP_RECEIPT.json.
- src/bass_he/{geometry,rotation,transport,eq54}.py
- src/arseny_reimpl/{cross_section,rotational,eq50_scoped}.py
- scripts/r10a_rho_freeze.py::_source_identity.

The code reconstruction in audit_support.py is explicitly an isolated dependency facade, not a full repository scientific run. An unchanged archived R10D adapter is included as a fixture and its blob is checked before loading its definitions.

## SciSpace discovery and primary web checks

A semantic query on smooth endpoint boundary layers versus actual singularities retrieved:

- Johnson, Algorithm 988 / AMGKQ, ACM TOMS 2018, DOI 10.1145/3157735; author preprint https://arxiv.org/abs/1410.1064 . Primary abstract describes simultaneous integrands, coordinate transformations and internal breakpoints. It does not prove our Coulomb integrand has a singularity or certify our tolerance.
- Sidi, Variable transformations and Gauss-Legendre quadrature for integrals with endpoint singularities, Math. Comp. 2009, DOI 10.1090/S0025-5718-09-02203-0. Discovery metadata/abstract only; not used to assert an endpoint singularity in BASS_HE.
- Zadorin and Zadorin, Quadrature formulas for functions with a boundary-layer component, 2011, DOI 10.1134/S0965542511110157. Discovery abstract only: high gradients can degrade classical fixed rules.

Primary implementation documentation actually opened:
- https://www.netlib.org/quadpack/dqagpe.f : known breakpoints, greatest-estimated-error interval subdivision, and explicit budget/nonconvergence statuses. Our vector callback and q map are not a claim of reproducing all of DQAGPE, nor is our embedded estimate rigorous.
- https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.integrate.solve_ivp.html : DOP853 is an eighth-order explicit Runge-Kutta method supporting complex ODEs; local error control is not a theorem certifying this entire program.

## Fresh Wolfram calculations

First expression used a=symbolic positive, b=sqrt(a^2+rho^2), R=a+b*cosh(eta), phi=2*atan[rho*tanh(eta/2)/(a+b)] and t=(a*eta+b*sinh(eta))/v.
Returned orbit, dphi/deta-rho/R, dt/deta-R/v residuals: 0,0,0. Returned head-on limit: a(1+cosh eta).
The first evaluator also emitted Symbol::undefined2 and MinValue/MaxValue warning messages. Those warnings were not suppressed or recast as a clean invocation.

A second fresh call used rational half-angle variables k=tanh(eta/2) and rho^2=(b-a)(b+a):

    radial = a+b*(1+k^2)/(1-k^2)
    cosine = (1-rho^2*k^2/(a+b)^2)/(1+rho^2*k^2/(a+b)^2)

Factor[Together[rho^2/(b*cosine-a)-radial]] returned 0.
Factor[Together[(1-k^2)/(a+b)/(1+rho^2*k^2/(a+b)^2)-1/radial]] returned 0.
FullSimplify[D[(scale*Sinh[q])^2,q]-scale^2*Sinh[2q]] returned 0.
This second call returned no warning message.

The independently implemented full-matrix DOP853 auditor verifies the numerical change of ODE representation; it is not an independent scientific reviewer. All R10G probes are outcome-informed authoring-side research.
