# BASS_HE HE-NONTHERMAL-D-BIRTH-01: bounded source-only ledger

**Original DAG:** BASS_HE 28/88; PAIR-COUNT15 local 14/18 (unchanged). Source branch pinned to `ffe384d06e6b300d2a7ef2adbaa7a50351c4e6ce`. Original 15 source rows are reused, not re-executed.

The 330 MeV target-rest frame fixed-mass event 4He + gamma -> D + D has A = 3727.3794118 MeV, M_D=1875.612945 MeV, E_gamma=330 MeV. Per-event daughter energy K0=(A+E_gamma)/2-M_D=153.0767609 MeV; rest mass energy change = 2 M_D-A =23.8464782 MeV. The sum of source energy contributions is exactly zero:

`(-A+2*M_D+2*K0-E_gamma)*R*(MeV_to_J)=0`, where `R` is an externally provided exclusive event density rate [m^-3 s^-1], still missing here.

`S[n_He4]=-R`, `S[n_Dfast]=2R`, `S[n_gamma]=-R`, giving baryon and charge residuals exactly zero. For a single incident direction n, the total D momentum injection equals `+E_gamma R*n/c` and photon loss is `-E_gamma R*n/c` after SI conversion. Individual daughter pressure/stress requires a separate angular provider.

These are only source contributions. Neither expansion transport, thermalization, energy deposition, actual cross sections, photon distribution, effective event normalization, named physical pool admission, nor full cosmological evolution is implemented or inferred. Missing rate is null, not zero. The manufactured-rate path remains `physical_activation=false`, `L4=false`, production `HOLD`.

CAS: Wolfram six exact-zero algebraic identities including covariance determinant (current session). Python: 18 new scoped tests PASS. Plotted 31 manufactured rates, exact energy residual zero and flipped-photon-sign mutation nonzero. Distinct native independent R6/C9: NOT_RUN. Previous original PAIR-COUNT15 19 tests are historical and not replayed.

Rice et al., Physical Review C 61, 064612 (2000), DOI:10.1103/PhysRevC.61.064612 covers 150-250 MeV, not a validated 330 MeV rate. All 330 MeV source-normalization and thermalization work remains explicit.

Next: verify qualified exclusive differential rate + photon field + frame and error, then add separate fast-D transport and thermalization interfaces. No original DAG advancement is claimed.
\n\n## Additional finite-mass pressure-trace partial-identification theorem (derived 2026-10-29)
Define CM invariant squared energy `s=A^2+2*A*E_gamma`, `E0=(A+E_gamma)/2`, `B2=E_gamma^2*(s/4-M_D^2)/s`, all using frozen target-rest MeV inputs. For the two daughter lab total energies `E±=E0±sqrt(B2)*mu`, the sum of their finite-mass kinetic stress traces (per event) is:
```
T(mu) = sum_±[(p_± c)^2/E_±] = 2*E0 - 2*M_D^2*E0/(E0^2 - B2*mu^2) [MeV].
```
This is NOT the same as the pair kinetic energy, physical temperature, total pressure tensor or realized rate. Suppose only a nonnegative angular distribution on `-1<=mu<=1` with known `m2=E[mu^2]`, 0<=m2<=1. Set `a=E0^2`, `b=B2`, 0<b<a. `f(x)=1/(a-b*x)` has `f''(x)=2*b^2/(a-b*x)^3>0`. Therefore, for any such angular distribution:
```
T_lower = 2*E0-2*M_D^2*E0*((1-m2)/a + m2/(a-b))
T_upper = 2*E0-2*M_D^2*E0/(a-b*m2)
T_upper-T_lower=2*M_D^2*E0 * b^2*m2*(1-m2)/(a*(a-b)*(a-b*m2)) >= 0.
```
This interval is universal and optimal for the unrestricted class of nonnegative symmetric angular probability measures: `mu=±sqrt(m2)` attains the upper endpoint, while masses `1-m2` at `mu=0` and `m2/2` at each `mu=±1` attain lower. Those atomic laws may not belong to the old *restricted sextic polynomial angular family*. Do NOT claim the endpoints are sharp for that polynomial family. Also no event/thermal rate is implied.

At the frozen FULL witness `m2=24377/71485` from the prior source, fresh exact-Fraction numerics yield:
```
T_lower = 588.113334807457 MeV/event
T_upper = 588.113999573142 MeV/event
width = 0.000664765685910278 MeV/event
relative width ≈ 1.130334741891487e-6
```
The range is not zero; one second angular moment does not identify the exact trace. The full tensor also requires azimuthal data. This remains a conditional source-only bound, not physical emission/transport validation. Wolfram checked the convex derivative and exact rational Jensen-secant gap identities, both with zero algebraic remainder. New Python test group `test_conditional_pressure_trace.py` 8 PASS (total 28 new isolated tests); plot `results/pressure_trace_moment_gap.png` was generated and visually checked. The curve peaks in the interior and vanishes at `m2=0,1`, as required by formula. The figure reports only a mathematical universal moment gap, not a measured cross section.
