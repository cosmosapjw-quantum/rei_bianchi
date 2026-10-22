# Tritium source audit: frozen bounded physics contract

Base: PR219 head `215d5c33a9a6fc9940ead91c29128f2c6f20b5b2`. The 82 existing quotient NPZ histories are immutable background inputs; the existing 83 IVPs and 13 figures are not rerun. Scope is conditional, passive-tracer postprocessing, not production-default adoption or a full nuclear network.

## R1 — Question and decision

Determine separately (a) why the old executable reports exactly zero T; (b) whether the listed D(D,p)T reaction has a positive source for positive ionized deuterium; (c) the magnitude of a stated bare-ion thermal model; (d) cumulative births versus surviving inventory. Old hard zeros are implementation/initial-condition choices, not a physical selection rule. A positive source disproves exact zero within its declared model even when a floating-point exponential underflows.

## R2 — Inputs and finite support

Use each saved `x,z,conditional,census,diagnostics,diagnostic_names`, with `T_K`, `nB_m3`, `H_per_s`, `elapsed_s`, `ne_cm3`; `D_0+D_1=Y_D`, `D_1=Y_D f_HII`. Check names, monotone time, positive H/T/nB and nonnegative ion populations. UV photons have support 5–60 eV; the listed nuclear photodisintegration thresholds are MeV. Their forward photo-source integrals vanish. This fact says nothing about charged-particle fusion tails or reverse capture coefficients.

## R3 — Conditional cross-section model

For unpolarized bare DD ions set `mu=m_deuteron/2`, `Z1=Z2=1`, `E_G=2 mu c^2 (pi alpha)^2`, and

`sigma_c(E)=S_c/E * exp[-sqrt(E_G/E)]`, `c=p,n`.

Nominal constants are `S_p=50.8 keV barn`, `S_n=51.0 keV barn`, from Viviani et al. (2023), DOI 10.1088/1742-6596/2586/1/012076, p.3. Authors' ±1.9/±1.4 are preliminary theoretical cutoff-spread estimates, not probability distributions. The constant continuation is OUR low-energy approximation, not their validated rate fit. Optional explicitly labeled sensitivity: DDp `S_p=56.7 keV barn` (Li et al. 2015, DOI 10.1103/PhysRevC.92.025805, arXiv:1503.08672). Published ±2.0 must not become a 99% low-temperature bound. No Bosch–Hale/BBN temperature-fit extrapolation is admitted. No plasma screening, bound-electron fusion, molecular, suprathermal-tail or acceleration model is implied.

## R4 — Maxwellian rate and numerical representation

For the declared common ion temperature T,

`k_c(T)=sqrt(8/(pi mu)) (kB T)^(-3/2) integral_0^infty S_c exp[-E/(kB T)-sqrt(E_G/E)] dE`.

Use SI inside the integral (`1 keV barn=1e3*eV_J*1e-28 J m^2`); k is m^3/s. Transform `E=E0*u`, where `E0=(E_G*(kB*T)^2/4)^(1/3)` and `a=E0/(kB*T)`. The integral is `S_c E0 exp(-3a) integral_0^infty exp[-a*(u+2/sqrt(u)-3)]du`. Integrate the shifted positive kernel, or a mathematically equivalent log-energy quadrature, and retain `log k`. Typical E0 is only a few to tens of eV, below direct/THM keV measurements. Numerical precision does not remove this model uncertainty. Report E0 range rather than claiming measurement coverage.

## R5 — Source counts and conservation

`s_c=R_c/nB=0.5*nB*(Y_D*f_HII)^2*k_c`, in baryon-normalized nuclei per second. The 1/2 is for identical reactants. Each DDp event consumes 2D and makes T+p; each DDn consumes 2D and makes He3+n. A-weighted stoichiometry is exactly conserved. Trace postprocessing leaves the original background unchanged; it is an approximation justified only by reporting integrated D-depletion `2*(C_p+C_n)/Y_D`. Also compute the all-D same-kernel comparator `s_c_allD=0.5*nB*Y_D^2*k_c`. This bounds the ion-selected source for this kernel; it is NOT a bound on real neutral/screened reactions.

## R6 — Fast decay and exact reconstruction convention

Root supplies source-pinned tritium half-life and neutron mean lifetime in `EVALUATED_DECAY_INPUTS.json`; do not silently guess absent evaluated values. `lambda_T=ln(2)/t_half_T`; `lambda_n=1/tau_n`. For direct T with zero initial abundance,

`dY_T/dt=s_p-lambda_T Y_T`,

`Y_T(t)=integral_0^t s_p(v) exp[-lambda_T(t-v)]dv`, `C_p(t)=integral_0^t s_p(v)dv`.

No cosmological IVP is needed. Define the numerical reconstruction explicitly: source linearly interpolated in proper time between output nodes. Exact endpoint recurrence with `q=lambda*dt`, `F=(1-exp(-q))/q` is

`Y_b=exp(-q)Y_a + ((F-exp(-q))*s_a+(1-F)*s_b)/lambda`.

Use stable small-q series/expm1 and large-q branches, and logsumexp for nonnegative terms. This is exact for the declared interpolant, not for unobserved continuous histories. QSS `Y_T=s_p/lambda_T` is a separately labeled approximation, with comparison against this recurrence and the transient `s/lambda*(1-exp(-lambda*t))` in a constant-source positive control. Store logs for rates, sources, births, survival; any linear underflow is represented as underflow, never physical zero. True zero controls may have log sentinel null/-inf plus an explicit structural-zero flag.

## R7 — Secondary neutron route and bound ceiling

DDn neutrons are born energetic, approximately 2.45 MeV. Thermal He3(n,p)T coefficients cannot be substituted without a slowing/transport model. DDp tritons are also born near 1 MeV, so thermal atomic rates and rest-frame decay require declared approximations; beta time dilation is small but not solved here. The finite lane computes DDn births and optionally a no-capture neutron decay convolution. A first-generation counting envelope is `C_T_secondary <= C_n`, giving `Y_T_primary+secondary <= C_p+C_n` from zero initial inventories, if each DDn neutron converts at most once and no external sources/recycling/multiplication are allowed. This is a conditional first-generation no-decay envelope, not a full-network bound. D(T,n)He4 can recycle a neutron after a T conversion, so repeated secondary T births are outside this bound. No probabilistic 99% assertion is permitted.

## R8 — Total T versus atomic/ionic T

Primary result is `Y_T_total`, independent of how surviving T is partitioned between T I and T II. Do not lift with the old fixed-isotope quotient and do not set `T_I=Y_T*f_HI` by analogy. A diagnostic ONLY may assume instantaneous thermalization, bare-ion injection into T II, isotope-equal hydrogen atomic coefficients, and constant local rates. Put `r=alpha_H(T)*ne`, `g=gamma_HI`; the steady two-charge solution is

`Y_T_total=s_p/lambda_T`, `Y_T0=Y_T_total*r/(lambda_T+r+g)`, `Y_T1=Y_T_total*(lambda_T+g)/(lambda_T+r+g)`.

This explicitly includes decay competing with recombination. The actual energetic daughter thermalization/charge branching is uncomputed. Universally within this tracer definition `0<=Y_T0<=Y_T_total`. For decay charge bookkeeping under shell preservation, T charge q becomes He3 charge q+1 plus one beta electron; recoil, shake-off and energy deposition are not solved.

## R9 — Finite acceptance checks

1. Establish original hard-zero logic and observed zero census; establish DII>0 in at least one saved state.
2. Positive DDp and DDn source logs for every positive DII,T,nB sample; zero-D and zero-ion controls give structural zero.
3. Identical-reactant 1/2, DD stoichiometry A/Z conservation, SI conversion and source ratio `k_n/k_p=S_n/S_p` hold to relative 1e-12 (pure algebra; relaxed to 1e-10 if independent quadratures).
4. Independently tightened quadrature at 100, 1000, 10000 K agrees within 1e-7 in natural log rate; adaptive quadrature successful. No requirement for linear representability.
5. Exact constant-source convolution control agrees within relative 1e-10 for representable positive cases; recurrence is nonnegative and surviving inventory never exceeds cumulative births within 1e-10 relative or equivalent log comparison.
6. Report coarse-versus-refined integrated source estimates. Refinement uses known analytic T(x) and interpolated saved H/nB/f, and is a reconstruction-sensitivity check only. A 0.02 dex cumulative-birth difference is acceptable for the coarse magnitude claim; otherwise use one 4x refinement and label residual resolution limitation, without background rerun.
7. Report passive depletion and compare to 1e-6. If larger, stop passive-tracer admission; do not silently upgrade to coupled integration. No 99% confidence or full-network completeness claim.

## R10 — Execution limits and stopping rule

Allowed new paths: this research unit only. Reuse all 82 quotient histories; exclude the old 18-state reference from sweep counts. Zero new background IVPs. Maximum one nominal postprocessing sweep, one source-grid refinement sweep, targeted numerical controls, and at most one 4x refinement only if R9.6 fails. Up to six figures if needed. One authorized repair for a concrete failed check, then return the failure and artifacts to the controller. Finite questions are R1(a–d); adjacent full nuclear, nonthermal transport or low-temperature screening research is deferred. Outputs must identify conditional quantitative results, exact logical/stoichiometric results, source gaps, and no production-default change separately.
