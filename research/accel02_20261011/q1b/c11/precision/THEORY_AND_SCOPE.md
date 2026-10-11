# C11 same-formula entry precision

Evidence status: **derived**, **numerically checked**, **implementation-verified** for the scoped r=0 source arithmetic. This is not native closure admission or a full-history result.

## Preserved definitions

The immutable background coefficient inputs, loaded HM12 binary64 data, redshift-linear and log-energy-linear ordinate interpolation, source physical band [10,50000] eV, C2 fixed-q grid and both angle weights are unchanged. The initial UVB arrays are loaded from saved C2 evidence, not integrated again. This module refuses r!=0 explicitly. All quantities below are eV per initial reference cm^3, with source rates additionally per second.

Let v(t)/vi=1+A(cosh(omega t)-1)+B sinh(omega t), where A=1+Bbg/(2 Dbg vi), B=root_poly_i/(vi sqrt(Dbg)). The implementation uses the existing relative-volume increment and L(t)=ln R(t)=-log1p(increment)/3. For delta=t1-t0>=0,

    delta_v/vi = 2 sinh(omega delta/2)
                 [A sinh(omega(t0+delta/2))+B cosh(omega(t0+delta/2))]
    L(t0)-L(t1) = log1p((delta_v/vi)/(1+increment(t0)))/3
    R(t0)-R(t1) = exp(L(t1))*expm1(L(t0)-L(t1)).

These are algebraically identical to the prescribed hyperbolic background solution. This is a precision change, not a new background solution. At accepted native boundaries R0/R1 are still taken from the immutable provider, exactly; the stable/legacy roundoff discrepancy is reported and checked by unchanged1e-12 source/energy pairing.

## Source intervals and a direct offset

Within each fixed-q cell [a,b], x=ln(q/a). Physical energy/source bounds become x_bound=ln(E_bound/a)-L. A born cell with a=50000 and E_bound=50000 therefore uses -L directly, avoiding subtraction of two approximately50000eV values. The ratio logarithm uses log1p((E-a)/a). Native source knots retain duplicate rows and the same one-sided values, with zero-width jumps having zero measure.

The FLRW proper-source factor R^-3(1+z)^3 cancels exactly to (1+zi)^3. This removes redundant roundoff; the table profile is still evaluated at z=zi+(1+zi)expm1(L). On a segment x=xl+dx*u, f(u)=(1-u)f0+u f1, 0<=u<=1:

    N_segment = dx*(f0+f1)/2
    Q_segment = a exp(xl) dx*(f0*w0+f1*w1)
    D_segment = a dx*[expm1(xl)*(f0+f1)/2
                           +exp(xl)*(f0*v0+f1*v1)]

where wk=int_0^1 basis_k(u) exp(dx*u)du, vk=wk-1/2. The positive v0/v1 series starts at order dx and avoids subtracting1/2. D is integral(q-a) dN; positivity follows from q>=a and the unchanged nonnegative profile.

Time quadrature shares positive16/32 Gauss nodes for N,Q,injected energy, radiation work and D. Source work is integrated directly as (R(t)-R1) SQ, never defined as a ledger residual. Physical existing-photon work uses stable deltaR*Q0. The original1e-10 per-cell own-fine criterion and1e-12 pairing remain unchanged; D additionally reports/passes the same local diagnostic comparison.

## Critical state limitation

D is returned only as a diagnostic; N and U remain the authoritative state. D is not silently fed into mean reconstruction, absorption, native cross sections or checkpoints. Rounding back to Q and then forming Q-aN loses digits in the thin born cell, as the preserved measurements show. Any future authoritative D/low-Q state needs consistent absorption evolution and checkpoint arrays/identity; this work does not provide those. The frozen generic physical-q endpoint/width guard remains active. In extremely short intervals where the immutable R endpoint rounds to1, source arithmetic can still resolve a birth but native support may reject it; this is a fail-closed limitation, not permission to seed/floor the moment.

## Independent reference and observed bounds

`reference_mp.py` independently evaluates the same binary64 coefficient/table inputs at80 decimal digits using mpmath1.3.0; it does not call the production moments or logR routines. It shares the physical input and interpolation equations and is not independent physical data. Its cell integrals use arbitrary-precision antiderivatives; actual born-cell time integrals use mpmath quadrature, not the production Gauss nodes.

The new actual intervals5e9 and2.5e9s were selected from the preserved C10 rejection evidence, then executed with changed arithmetic. Old unchanged time scans were not replayed. Maximum16/32 differences are1.3540307934490514e-15 and1.2186277301915167e-15, respectively; max source-plus-redshift pairing3.010387400797818e-16. The five born-cell integrated quantities agree with the80digit reference to1.4866059165842225e-15.

At the first midpoint, old source-band reachable-width and ray-difference relative errors were6.7291e-10 and5.9473e-10; stable formulas yield1.4483e-16 and2.3269e-16. At the second midpoint, the old ray difference error1.3285e-9 becomes2.9481e-16. This localizes real floating-point loss, rather than attributing every rejected pair to unresolved time quadrature.

The directly integrated D agrees to<=1.04e-16 for these intervals; rounded Q-aN differs by1.02e-10 to3.56e-10. The source repair therefore resolves the measured source-time rejection but does not certify the native thin-support reconstruction.

## Actual work and nonclaims

Three new targeted tests passed: short/late-time stable ray differences; direct birth offset against80digit reference including a witness of lost Q-aN digits; explicit non-FLRW refusal. First missing-mpmath environment failure, missing-implementation RED, and GREEN are preserved. The test subprocess exit status was not captured separately from the shell's final cat; raw unittest GREEN log records3 tests/OK. Actual source driver exit0 is separately available from its shell invocation. Old RUN002/EVENT003/Q0, C3 opacity/partition scans, old native family and old checkpoint suites were not run. Native gas and SIGMA calls0. No full15.9->4 history or scientific temporal/spectral admission is claimed.
