# RR/Mao finite-temperature enclosures: source contract and constructive derivation

Unit: rei_rr_mao_finite_temperature_enclosure_20261028.
Workflow: physmath-research-loop 1.0.0. Author: /root.
Question: enclose the represented-real six-row RR rate and the actual selected Mao2017 hybrid kinetic-loss function over every closed temperature interval in 100..1e6 K; derive a finite log-temperature Taylor remainder for both quantities.

This is the next explicitly requested unit. The preceding DR unit has actual accepted numerical evidence and a pending figure. No new IVP is part of this unit. Numerical execution and saved-data rendering have separate outstanding resource obligations. Theory below does not depend on executing the implementation.

## 1. Source identity, semantics and conventions

The actual native route is the fixed REI PR237 source at ee6746ab172f862dddfdec63b59e5e3707b59eaa, with PR241 chemical return 41d2d92a186659f39cc2af60f26eba97972b6e82 and VigilODE actual-model derivative 36104bfc65d1fdc695c8acea383c54b50a1c4e78 retained as distinct dependencies. The latest completed census observed these substantive tips unchanged. Complete local source copies are carried into source/ with individual byte identities.

The coefficient input atomic_coefficients.json has SHA256 38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc and Git blob 2eba600a9d7a7359ca55f566f1b841a363a3e5c7. Each JSON number is decoded as Python/native binary64, and its exact real image is the coefficient used here. The same rule applies to the source constants s=Float64(1e-6), k=Float64(1.380649e-23), and eV_J=Float64(1.602176634e-19). The source constants' nominal units are respectively m^3/cm^3, J/K and J per eV.

Admitted recombining keys are 1:1,2:1,2:2,3:1,3:2,3:3, meaning (nuclear Z, initial ionic q). For Mao the source table index is recombined electron count n=Z-q+1; preserve that mapping. All six RR and selected Mao rows are present. An unknown key is an error, not a zero channel. Nonfinite, boolean, complex, reversed and out-of-domain temperature inputs are refused. The closed common domain is exactly [100,1000000] K. Accepted decimal-string inputs denote their exact decimal real value; binary64 inputs denote their exact binary64 image. No intermediate native floating rounding map is identified with the differentiable real function.

All logarithms are natural. Positive powers are exp(exponent*ln(base)). Temperatures in RR square roots are ratios of quantities in K. The Mao log argument is the dimensionless numerical temperature in eV, tau=k*T/eV_J. No logarithm of a dimensional quantity is used. Alpha has units m^3/s; L has units J m^3/s, so n_e*n_ion*L is a proper-volume kinetic-energy loss in W/m^3. Ionization binding energy has a separate owner in ThermalSources and is absent from L. The metric convention, if needed downstream, is (-,+,+,+); no c=1, hbar=1 or k_B=1 convention is imposed here.

The native ThermalSources constructor defaults to rr_closure='mao2017'. Its chosen loss is k*T*alpha_native*f_Mao. The alternate rate-derivative loss k*T*(3 alpha/2 + D alpha) is a different conditional closure. It is not substituted here. Point temperature derivatives already exist in the native code: this work supplies finite-box and finite-step bounds, not a newly invented missing point-JVP requirement.

The full mao2017_selected.json original includes prior table comparisons, closure-difference numbers and f_at12000 evaluations. They are preserved as source-embedded historical evaluation exposure, not initial findings of a new reviewer and not results of this unit. The meaning of the rows and unfavorable source evidence are not redacted. Their fitted residual percentages are not an uncertainty enclosure for derivatives or for this hybrid.

## 2. RR definition and actual coefficient conditions

Write D=T*d/dT, z=T2/T, u=sqrt(T/T0), v=sqrt(T/T1),
b=B+C exp(-z), p=u/(1+u), q=v/(1+v), and lambda=ln(1+u)-ln(1+v).
The represented-real rate is

  alpha(T)=s*A/[u*(1+u)^(1-b)*(1+v)^(1+b)].                 (RR0)

The six nominal source rows, before exact binary64 decoding, are:

| key | A (cm^3/s) | B | T0 K | T1 K | C | T2 K |
|---|---:|---:|---:|---:|---:|---:|
|1:1|7.982e-11|0.748|3.148|703600|0|0|
|2:1|3.294e-11|0.691|15.54|36760000|0|0|
|2:2|1.891e-10|0.7524|9.37|2774000|0|0|
|3:1|8.7e-12|0.364|147|7153000|0.1508|715400|
|3:2|9.349e-11|0.6916|34.7|7329000|0.0351|629300|
|3:3|2.867e-10|0.7493|21.08|6268000|0|0|

They satisfy A>0, T1>T0>0, T2>=0, C>=0, 0<B<=b<=B+C<1, with strict margins that also hold for their actual binary64 images. Thus RR0 is smooth and strictly positive for T>0. No clipping or coefficient alteration occurs.

Set b_1=D b=C*z*exp(-z) and b_2=D^2 b=C*z*(z-1)*exp(-z).
Since D u=u/2, D v=v/2,

  D p=p(1-p)/2, D q=q(1-q)/2, D lambda=(p-q)/2.          (RR1)

Differentiate the dimensionless normalized logarithm
ln(alpha/(s*A))=-ln u-(1-b)ln(1+u)-(1+b)ln(1+v). Product differentiation gives

  r_1=D ln alpha
     =-1/2-[(1-b)p+(1+b)q]/2+b_1*lambda,                (RR2)
  r_2=D r_1
     =-[(1-b)p(1-p)+(1+b)q(1-q)]/4
       +b_1*(p-q)+b_2*lambda.                          (RR3)

For clarity, differentiating the b-dependent bracket contributes b_1*(p-q)/2; differentiating b_1*lambda contributes another b_1*(p-q)/2 plus b_2*lambda. This produces the full b_1 coefficient in RR3. In particular the Li correction is not frozen while taking derivatives.

It follows exactly that

  D alpha=alpha*r_1,
  D^2 alpha=alpha*(r_1^2+r_2).                          (RR4)

## 3. Strict monotonicity for these actual RR rows

For T1>T0, u>v, hence p>q, lambda>0 and D lambda>0. Moreover

  0<lambda<ln(u/v)=(1/2)ln(T1/T0).

The upper inequality follows from (1+u)/(1+v)<u/v. For z>=0 the elementary maximum z exp(-z)<=1/e gives b_1<=C/e. Since the bracket in RR2 is positive,

  r_1 < -1/2 + [C/(2e)] ln(T1/T0).                     (RR5)

Thus C ln(T1/T0)<e is a sufficient global strict-decrease condition. It is immediate for C=0. It also holds for both nonzero-C rows without a sampled scan or numerical logarithm:

- 3:1: the exact coefficient images satisfy C<151/1000 and T1/T0<2^16. Hence C ln(T1/T0)<(151/1000)*16*(7/10)=1.6912<2.7<e.
- 3:2: C<36/1000 and T1/T0<2^18, so C ln(T1/T0)<(36/1000)*18*(7/10)=0.4536<2.7<e.

The elementary inequalities ln 2<7/10 and e>27/10 follow, for example, from positive exponential series: exp(7/10)>1+7/10+(7/10)^2/2+(7/10)^3/6>2 and e>1+1+1/2+1/6+1/24>2.7. The loose rational coefficient margins are deliberately much larger than one binary64 rounding step.

Therefore every contracted RR row is strictly decreasing on T>0, in particular on the common domain. For any I=[Ta,Tb] in that domain,

  alpha(I) = [alpha(Tb),alpha(Ta)]                     (RR6)

as an exact real image. Directed point evaluation encloses these two endpoints. It is not necessary to infer monotonicity of the Mao factor or of L.

## 4. The selected Mao factor and its log derivatives

Use distinct symbols for Mao fit parameters (a0,b0,c0,a1,b1,a2,b2); they are the exact images of the original row fields. In this section b1 and b2 without underscores denote Mao constants, not the RR derivatives b_1,b_2. Set

  ell=ln(tau), tau=k*T/eV_J,
  U=a1 exp(-b1*ell), V=a2 exp(-b2*ell),
  P=U/(1+U), Q=V/(1+V).

The actual selected formula is

  f(T)=a0 exp(-b0*ell-c0*ell^2)*(1+V)/(1+U).            (M0)

All selected rows have a0>0, a1>=0, a2>=0 and finite parameters. In particular 3:1 has c0=Float64(0.007567), and 2:1 and 3:1 have nonzero a2. This matters to derivative and interval coverage. Since tau>0, U,V>=0, both denominator and numerator are strictly positive. Thus f is smooth and positive, including the a2=0 and b2=0 rows; no ln(a2) is needed.

Because D ell=1, D U=-b1 U and D V=-b2 V,

  D P=-b1 P(1-P), D Q=-b2 Q(1-Q).

Differentiating ln(f/a0)=-b0 ell-c0 ell^2+ln(1+V)-ln(1+U) yields

  m_1=D ln f=-b0-2*c0*ell-b2*Q+b1*P,                  (M1)
  m_2=D m_1=-2*c0+b2^2*Q(1-Q)-b1^2*P(1-P),           (M2)
  D f=f*m_1, D^2 f=f*(m_1^2+m_2).                     (M3)

These formulas preserve the natural-log convention and the T_K-to-T_eV conversion. An eV change of numerical argument is not absorbed into the fit parameters.

## 5. Selected kinetic loss, positive boxes and curvature

The chosen hybrid is

  L(T)=k*T*alpha(T)*f(T).                              (L0)

It has the same source definition as ThermalSources(...,rr_closure='mao2017'), at the represented-real-function level. Since every factor is positive on the compact contracted domain, L>0.

Let w=1+r_1+m_1. Then

  D L=L*w,                                           (L1)
  D^2 L=L*[w^2+r_2+m_2].                              (L2)

Indeed D ln L=1+r_1+m_1 and D w=r_2+m_2. A third derivative of the RR log rate is unnecessary for this selected Mao loss; it would arise for the different rate-derivative closure.

Construct outward interval operations on any I=[Ta,Tb]:
1. Bound u,v,z,b,b_1,b_2 and r_1,r_2 using RR1–RR3. Monotone primitive interval images and inclusion-preserving arithmetic suffice. The narrower endpoint image of lambda may be used because D lambda>0.
2. Evaluate alpha's two monotone endpoints through RR6.
3. Bound ell,U,V,P,Q and the exponential in M0 by inclusion-preserving arithmetic, keeping the squared-log term. The factor box has a strictly positive lower endpoint when representable; no inference from endpoint maxima of f is required.
4. Bound m_1,m_2 from M1–M2.
5. Form the positive loss box [k]*I*[alpha(I)]*[f(I)], and second-derivative boxes from RR4 and L2.

Repeated variables can make the natural interval bounds conservative, especially across the whole domain. Dependency does not invalidate enclosure. Intersecting with a mathematically justified sharper bound is optional, but no unproved clipping or fitted tolerance repairs an invalid range. The derivative boxes may straddle zero; positivity refers to alpha/f/L, not to their derivatives or to every standalone Taylor enclosure.

For either y=alpha or L, let J2_y be its computed outward interval for D^2 y over I and set

  B2_y=max(abs(lower(J2_y)),abs(upper(J2_y)))            (B0)

with upward rounding. Then B2_y bounds |D^2 y(T)| for every T in I. This is a uniform continuum consequence of the formulas and inclusion operations, not merely sample containment.

## 6. Log-temperature Taylor theorem with arithmetic enclosure

Choose an exact admitted anchor Tstar and target Ttarget in I. Define h=ln(Ttarget/Tstar), and y_tilde(x)=y(Tstar exp(x)). The whole connecting log segment lies inside I because positive geometric interpolation stays between its endpoints. The fundamental theorem of calculus twice gives the first-order Taylor remainder; for either sign of h,

  | y(Ttarget)-y(Tstar)-D y(Tstar)*h | <= B2_y*h^2/2.   (T0)

For h<0 one can reverse the integration limits, or set x=-s; the absolute-value bound is unchanged. C^2 smoothness on an open neighborhood of the positive compact interval was established above.

In implementation, outward base interval Y0, derivative interval Y1 and log interval H enclose y(Tstar),D y(Tstar),h. With hmax=max(abs(H.lo),abs(H.hi)) and upward rho=B2_y*hmax^2/2,

  Y0 + Y1*H + [-rho,rho]                              (T1)

encloses y(Ttarget). The actual stored h, f0, derivative, curvature bound and radius are part of each returned record; reporting the analytic remainder alone must not discard arithmetic uncertainty.

When Ttarget equals Tstar exactly under the input encoding, return exact H=[0,0], rho=0 and enclosure=Y0. This avoids manufacturing a nonzero or underflow-sensitive radius for a true zero step. The derivative can still be returned. Unequal targets use the full enclosure; no equality tolerance is used.

## 7. Discriminating exact controls (R7 theory input)

These analytic controls are available independently of any program evaluation.

A. Coalescent scale limit T0=T1 makes u=v, lambda=0 and p=q. All b-dependence cancels in RR0, yielding alpha=s*A/[u(1+u)^2]. At u=1:
alpha=s*A/4, r_1=-1, r_2=-1/8, D^2 alpha=7 alpha/8.
This is a declared manufactured continuous-limit control, not a modification of an actual row or an extension of the strict T1>T0 source validator.

B. If a1=a2 and b1=b2, the Mao ratio cancels identically. Then f=a0 exp(-b0 ell-c0 ell^2), m_1=-b0-2c0 ell and m_2=-2c0. At ell=0, f=a0. This detects an omitted c0 curvature term without numerical fitting.

C. For actual Li rows, at T=T2 (within the common domain), z=1 and b_1=C/e>0, lambda>0. Freezing b while differentiating would omit the strictly nonzero term (C/e)*lambda from r_1. A point-rate match therefore cannot establish the derivative contract.

D. The native-selected loss and the alternative derivative moment differ by the factor f_Mao-(3/2+r_1). Their source functions are distinct. Equality is not assumed, and a source comparison is not a physical uncertainty distribution.

E. The h=0 result is exact; positive and negative h have the same quadratic bound. A dyadic step h/2 reduces the same uniform bound radius by exactly one quarter before rounding. This does not assert an observed convergence result until actual outputs exist.

An optional bounded CAS check may verify polynomial identities for RR3, M2 and L2. It is supplemental to the full derivation, must retain exact input/output/timing and does not act as a native reviewer. The numerical implementation controls and figure remain distinct later obligations.

## 8. Source meaning, literature and deliverables

The Verner–Ferland author data page (https://www.pa.uky.edu/~verner/rec.html) and Badnell author RR page (https://amdpp.phys.strath.ac.uk/tamoc/RR/) define the rate-fit family and the low-charge b correction. Badnell2006 arXiv:astro-ph/0604144 identifies its underlying ADAS temperature grid and total-rate fitting context. Mao, Kaastra & Badnell2017, DOI10.1051/0004-6361/201629708, supplies the weighted electron kinetic-loss factor. The selected project source controls the six exact rows, common domain, natural-log convention and hybrid use. Author formula identity is used; no published rate-fit accuracy percentage is promoted to a rigorous derivative, hybrid or physical-temperature error bound.

The new contribution within this project is the constructive finite-box and finite-log-step enclosure for these pinned represented-real RR/Mao functions, plus executable directed arithmetic. It is not a literature novelty or strong no-go claim. NG1–NG7 therefore do not establish a new exclusion theorem.

Required code API: range(key,lo,hi,quantity='alpha'|'loss'), point/first derivative, uniform_second_bound, taylor(key,Tstar,target,domain,quantity); returned numeric values must retain exact endpoint strings, source identity and scope. Reuse the pinned DR Arithmetic/Interval semantics only with explicit identity and context bounds. Any new primitive must state its rounding enclosure. Pure caching may reuse immutable results only under complete operand/context/source keys with fresh mutable wrappers.

Actual numerical acceptance will require meaningful selected raw direct-oracle containment, temperature correction cases, natural-log/c0 and a2 paths, precision consistency, finite interval and two-sided Taylor records, zero-step and source/input refusal records. No test-count threshold is a scientific proof. The independent scalar oracle may share Decimal/libmpdec, which must be disclosed rather than described as different-library validation. A saved-data figure must display the appropriate source units and domains without recomputing science.

Physical fitting uncertainty, actual REI recipient temperature, native25 state and physical radii remain null; L4_ready=false and global_physical_completion=null. Existing original DAG admission remains working33/88,central28/88,88IDs/17edges,delta0. No new physical node follows from this local theory or its later coding-stage count.

