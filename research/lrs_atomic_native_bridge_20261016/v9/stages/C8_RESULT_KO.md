# V9 C8: source / opacity / chemistry time-order isolation

**Physical scope**: Manufactured smooth source (S(X)) and rate (lambda(X)) in fixed-energy 0D photons and HI/HII stocks, per *total* hydrogen nucleus; (X=\ln(a/a_0)). No Grackle RR, real stellar spectrum, redshift work, native PR150, or physical EoR history. Source: PR #168 at `c02fb3492b99b79c8b2e3bae1a6183510ff1df9b`.

Python 3.13.5 / NumPy 2.3.5 / SciPy 1.17.0, direct `solve_ivp(method="Radau",rtol=1e-12,atol=1e-14)` independent RHS. **61/61 pytest PASS**. Actual C8 sweep: five problems × six numerical variants × N in {8,16,32,64,128,256}, exactly **180 numerical rows**. Machine-readable full rows are reproducible via `python run_study.py`.

## Source/opacity both varying, dynamic HI stock

| Variant | photon |N256 − N_Radau| | last observed p |
|---|---:|---:|
| S(mid), lambda(mid), exact pair, S half/half | 4.0867843e-07 | 1.999992 |
| S(left), lambda(mid) | 1.9614122e-04 | 0.996894 |
| S(mid), lambda(left) | 1.3588696e-04 | 1.005172 |
| both left | 6.0717332e-05 | 0.989347 |
| all births at panel start | 4.3077464e-04 | 0.998190 |
| pair backward Euler, others midpoint | 5.4371951e-04 | 0.997587 |

Maximum absolute saved photon/atom/ion/energy ledger residual over 180 rows: `4.618527782440651e-13` (mixed units, dominated by fixed-energy bookkeeping); stocks nonnegative. These algebraic ledgers do **not** certify accuracy. Max `k*h*M0` of the deliberately strong opacity probe N8 ≈2.033; do not infer uniformly stiff convergence.

Wolfram R5 local truncation shows one-sided source error -S′ h²/2; one-sided opacity error +k′N h²/2; batching births at start error −k S h²/2. Both first-order terms can cancel at one h: **both-left can appear more accurate in amplitude than either one-lag variation while remaining first-order**. Also the exact manufactured proportional S/k with affine k produces floating-point near-zero error for any h under midpoint integration. An initial incorrectly monotone exact-case assertion failed; diagnosed this analytic cancellation and replaced it by an exact-branch regression without relaxing tolerance.

**Native owner causal attribution remains HOLD.** A correct source-on owner test must use actual PR150 fixed_step and frozen donor/clock, with source/opacity/BE flags independently varied and all photon/chemical/thermal/binding/escaped/geometry work events kept by single owner. PR #167 old/newborn, BASS_HE HE25/26 moving birth-cut, bass_cr C21B source-age are neighboring results, not replacements for this factual native test.

Scientific sources: [Mackey 2012 A&A 539 A147](https://doi.org/10.1051/0004-6361/201117984) describes time-centred photon-conserving raytracing, not an empirical demonstration of this V9 owner's accuracy.
