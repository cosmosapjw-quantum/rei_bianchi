# RUN19: source-preserving temperature reuse and continuous interpolation bounds

## Result and scope

The existing REI temperature table is reused. The new mathematical result is a
set of explicit, continuous, smooth-branch derivative bounds for all 15 frozen
Grackle channels. These close the unknown-curvature premise of the earlier C8
ideal log-linear estimate and give a constructive error bound for a four-node
value-cubic accelerator on a uniform log-temperature grid.

| Numerical representation | Nodes over 1–10^6 K | Maximum relative truncation bound |
|---|---:|---:|
| Ideal log-linear, existing grid | 65,537 | 4.371181585181216e-7 |
| Ideal four-node value-cubic | 16,385 | 1.500359829631123e-6 |
| Ideal four-node value-cubic | 32,769 | 8.512614813784016e-8 |

All are below the original C9 coefficient target 1e-5. The bounds concern the
real functions defined by the source decimal literals, exact log-grid nodes,
exact source values at those nodes, and exact interpolating polynomials.
The rounded Rust representation has separate source-value, coordinate and
arithmetic errors, addressed constructively in Section 5. Root's Rust pilot
owns the actual sampled accuracy, timing and fallback evidence.

The computations took 0.01220 s and 0.02175 s. The exact polynomial-transform,
primary RR reference and manufactured interpolation tests passed 3/3 in 0.010 s.
This theory unit made no native gas call, IVP integration, spectral quadrature
or historical RUN13/RUN17/RUN18 re-execution.

## 1. Actual source reuse and ownership

The immutable source directory is
research/atomic_nuclear_ssot_20261017/run13/recovered/code/rei_bass_coupled.
Exact input identities are in the execution JSON. In particular:

- owner_src/igm_rates.rs: SHA256
  310164e620617f3089d488bd1f9668996b4a4cbd191383e45303def176ef81cf.
- owner_src/rate_table.rs: SHA256
  334e0da513b07ae78e8bbc669ac09b7c74dd9abec3c48934cbc94442c0cef8a6.
- owner_src/igm_thermal.rs: SHA256
  29fc785e20f1218578c90df4ef39a69de3577eb0b65585e86a6183328e0c75f1.
- owner_src/deuterium_atomic.rs: SHA256
  b9666efedf86c88e80a82ec412dc18a06bdc8d563c3786cc5001a63580422cf1.

igm_rates(T) is the explicitly selected Case-A subset of Grackle
af7939494ce65007887ada7b98d1813df6843346. Its package domain is 1–10^6 K;
this operational domain is distinct from the empirical support of each fit.
The source's 11605 K/eV conversion, Boltzmann constant, CI floor and CE caps
are preserved. The metric convention remains (-,+,+,+); c, hbar and k_B
have not been set to one.

Existing rate_table.rs already supplies 65,537 log-linear nodes, immutable
Arc sharing, coefficient-major storage, scalar/SoA/bounded-parallel evaluation,
source fallbacks and exact-temperature prepared bundles. C8 already gave the
conditional second-derivative lemma and sampled coefficient accuracy. C9
separated O(h^2) value errors from O(h) log-slope errors and corrected
worker-confounded performance claims. Those archived tests and timings were
read and reused.

The outstanding duplicate in the frozen consumer is concrete:
src/gas_reference_rhs.rs::gas_rates calls igm_rates(T) and then d_atomic_rhs,
whose provider.rates(T) prepares the same H coefficient bundle again.
DAtomicProvider::rates_from_prepared already projects the H-equality channels.
igm_point_rhs_with_prepared rejects a bundle whose temperature differs from
the recovered EOS temperature. Reusing one bundle at that exact T removes
repeated coefficient work without changing chemistry. The new native
integration of this contract is owned by the runtime agent.

### Coefficients and runtime factors

For a positive channel, write w_r=k_r(T)d_r(n), with density product d_r>=0.
The table owns k_r only.

| Native channel family | Source coefficient units | Runtime factor |
|---|---|---|
| CI, RR, DR number rate | cm^3 s^-1 | electron density × initial-ion density |
| H/He RR kinetic cooling, HI/HeII CE | erg cm^3 s^-1 | corresponding two-density product |
| Metastable-HeI CE coefficient | erg cm^6 s^-1 | n_e^2 n_HeII |
| Free-free | erg cm^3 s^-1 | n_e sum_q Z_q^2 n_q |
| D H-equality number rates | m^3 s^-1 | original H coefficient ×10^-6, then SI densities |
| D H-equality thermal coefficient | J m^3 s^-1 | original H coefficient ×10^-13, then SI densities |

The gas assembly converts erg cm^-3 s^-1 to J m^-3 s^-1 by 0.1 exactly.
D aliases H coefficient channels; their interpolation perturbations are
correlated through that shared bundle. D binding energy and its photo gate
remain caller/source inputs.

Savin charge exchange is a separate T-only owner on 2.7–200,000 K and is not
one of these 15 certified coefficient channels. Its forward fit is a
difference of positive terms: a future log-table extension must establish
positivity of that difference on each admitted domain. CMB power depends on
n_e, T_gamma^4 and T_gamma-T; photoionization depends on the radiation field
and atomic energy gate; expansion and geometry depend on time. These runtime
factors do not become T-only through coefficient caching.

## 2. Log variables, native branches and polynomial certificates

Let x=ln(T/(1 K)), f_j(x)=k_j(T)/u_j, and g_j(x)=ln f_j(x), where u_j is
the fixed unit coefficient used by that source channel. Differentiation in x
is D=T d/dT. The source polynomials use l=ln(T/(11605 K)); x and l differ
by a constant, so their derivatives agree.

CI HI, CI HeI, CI HeII and high-temperature RR HII have source form exp(p(l)).
The script parses the actual Rust polynomial expressions into rational
decimal coefficients. For each p^(r), r=1,...,4, it transforms each integer
subinterval into Bernstein form. The Bernstein basis is nonnegative and sums
to one; its minimum and maximum coefficients therefore enclose the polynomial
over the entire subinterval.

The enclosing intervals are [-2,5] for CI HI and [-1,5] for the other three,
wider than their positive source branches. For HI, all terms of p(l) are
negative when l<0, and p(l)<=p_0-2p_1<-50 for l<=-2. A positive rational
Taylor partial sum proves exp(2.5)>10, hence exp(-50)<1e-20. This range is
floor selected. Every term of p'(l) is positive for l<0, so the floor
crossing is unique: identical endpoint floor masks cannot hide two interior
crossings on that native floor-eligible interval. The other CI channels are
constant below T/11605<=0.8. RR HII's lower branch is the prescribed
HeII RR power law.

Source cuts are the 5500 K RR switch, nominal 9284 K CI/DR switch, and A/L
for A in {118348,13179,473638,470000,94000} K,
L=69.07755278982137, plus the HI floor transition. The operational f64
decision remains the frozen source comparison. A cubic support is rejected
if any of its three constituent cells crosses one of these cuts or changes
its floor/structural-zero identity. Edge cells without four support nodes
use the direct provider.

## 3. Analytic bounds for the remaining channels

The elementary identity used with the source polynomials is

D^2[c+p x-A exp(-x)-q ln(1+b exp(sx))]
= -A exp(-x)-q s^2 v(1-v),

where v=b exp(sx)/(1+b exp(sx)). For the logistic term, derivatives of orders
2,3,4 have absolute upper bounds |q||s|^r/4 because v(1-v)<=1/4,
|1-2v|<=1 and |1-6v+6v^2|<=1. The first derivative is bounded by |q s|.
A capped -A/T term is constant on its capped branch and satisfies
|D^r(-A/T)|=A/T<=L on the uncapped branch. These identities handle CE and
the rational RR/cooling denominators.

For the positive DR multiplier H=ln(1+0.3 exp(-u)), u=A/T, let
w=0.3 exp(-u)/(1+0.3 exp(-u)). Its first four Bernoulli cumulants have
absolute values at most w. The exponential chain rule gives

|D^r H| <= 0.3 sum_{k=1}^r S(r,k) k^k exp(-k),  r=1,...,4,

using max_{u>=0} u^k exp(-u)=k^k exp(-k). The Stirling rows S(r,k) are
{1}, {1,1}, {1,3,1}, {1,7,6,1}. Replacing exp(-k) by (3/8)^k gives exact
rational upper bounds, since e>8/3. Add the derivatives of -1.5x and the
first activation exponential. A capped activation factor is constant on its
capped branch.

For bremsstrahlung, set y=5.5-x/ln10 and
g=constant+x/2+ln(1.1+0.34 exp(-y^2/3)). Use the same cumulants with inner
derivatives 2y/(3 ln10), -2/(3 ln10^2),0,0. The maxima of
|y|^k exp(-y^2/3), e>8/3 and ln10>2 give the rational bounds below. The
r=2 bound uses w<=0.34/(1.1+0.34) for its constant-inner-second-derivative
term.

### Explicit smooth-branch derivative bounds

Each entry bounds |D^r ln(k/u)|. Exact fractions are retained in
execution02/CUBIC_RATE_BOUND.json.

| Channel | M1 | M2 | M3 | M4 |
|---|---:|---:|---:|---:|
| CI HI | 67.80194103 | 51.03960535 | 34.47173101 | 19.86026945 |
| CI HeI | 57.24189003 | 48.19507231 | 36.71547748 | 23.78179349 |
| CI HeII | 98.51568674 | 76.19286267 | 52.22093931 | 30.28549457 |
| RR HII | 1.17623784 | 0.12267094 | 0.03253885 | 0.04057838 |
| RR HeII | 0.6353 | 0 | 0 | 0 |
| RR HeIII | 1.4 | 0.1225 | 0.08575 | 0.060025 |
| DR HeII | 52.23330494 | 50.90205494 | 51.66670338 | 55.99619557 |
| CE HI | 69.57755279 | 69.14005279 | 69.10880279 | 69.09317779 |
| CE HeI | 69.74625279 | 69.14005279 | 69.10880279 | 69.09317779 |
| CE HeII | 69.97455279 | 69.14005279 | 69.10880279 | 69.09317779 |
| RR cooling HII | 2.318894 | 0.169913697 | 0.085296675894 | 0.042818931298788 |
| RR cooling HeII | 0.346 | 0 | 0 | 0 |
| RR cooling HeIII | 2.318894 | 0.169913697 | 0.085296675894 | 0.042818931298788 |
| Raw DR cooling | 70.69005279 | 69.35880279 | 70.12345123 | 74.45294342 |
| Free-free | 0.603030304 | 0.077988216 | 0.085858586 | 0.083712122 |

Displayed bounds are rounded upward; exact fractions are authoritative.
Active DR cooling reuses the raw coefficient above its reaction switch and
is exactly zero below. D's constant unit conversions leave these derivative
bounds unchanged.

## 4. Four-node value-cubic estimate

On x_i<=x<=x_(i+1), put theta=(x-x_i)/h and use support i-1,i,i+1,i+2:

w_-1=-theta(theta-1)(theta-2)/6,
w_0=(theta+1)(theta-1)(theta-2)/2,
w_1=-(theta+1)theta(theta-2)/2,
w_2=(theta+1)theta(theta-1)/6.

For f in C^4 over the entire support, interpolation gives

|f(x)-P3(x)| <= (3/128) h^4 sup_support |f^(4)|.

The nodal product equals u(2+u), u=theta(1-theta) in [0,1/4]. Its maximum
is 9/16, attained at theta=1/2; division by 4! gives 3/128. This interpolates
source coefficients, with no evolved observable correction.

Since f=exp(g),

f^(4)/f = g^(4)+4g'g'''+3(g'')^2+6(g')^2g''+(g')^4.

Define B4=M4+4M1M3+3M2^2+6M1^2M2+M1^4. Every support point is at
distance at most 2h from a central query, so sup_support f/f(query)<=exp(2hM1).
Consequently,

|P3/f-1| <= (3/128) h^4 exp(2hM1) B4.

Displayed evaluations use h=ln(10^6)/(N-1). Exact bounds use the larger
rational hbar=14.04/(N-1). A positive rational Taylor sum verifies
exp(2.34)>10, hence ln10<2.34. For every candidate/channel pair,
v=2hbar M1<1, and exp(v)<=1/(1-v) gives an exact rational majorant.
These operations yield the first table.

The support guards are premises. Finite positive computed P3 passes the
value-admissibility check. Accuracy follows from the quantitative estimate
or separately executed source comparison. The two negative exterior weights
can otherwise overshoot. With an ideal relative bound epsilon<1 and a
positive source, the ideal interpolant is automatically positive.

## 5. Nodal, coordinate and arithmetic perturbations

The weights satisfy the exact conditioning relation

sum |w_j| = 1+theta(1-theta) <= 5/4.

If supplied values obey |fhat_j/f_j-1|<=eta, their relative contribution is
at most (5/4) exp(2hM1) eta. Add this to ideal truncation. A future
floating-point certificate can therefore supply:

1. correct support and branch selection;
2. nodal relative error eta, including source evaluation and node placement;
3. log-query error delta_x;
4. weighted polynomial arithmetic error epsilon_arith.

For a query shift within the same admitted support, one sufficient total
bound is

exp(M1 delta_x) [epsilon_interp+(5/4) exp(2hM1) eta+epsilon_arith]
+exp(M1 delta_x)-1.

The formula identifies the remaining numerical quantities. Native libm
log/exp/pow and the root-owned interpolation arithmetic have no whole-domain
directed-rounding certificate from this unit. Their actual source comparisons
retain their stated sampled scope.

For log-linear interpolation, |g'-L'|<=M2 h/2 inside each cell: L' is the
average of g'; integrate M2|x-s| to obtain the bound. At interpolation knots
there are one-sided slopes. This supplies no globally smooth Jacobian API
and preserves C9's derivative policy.

## 6. Shared preparation, rate perturbation and gas feedback

At a fixed state, suppose |khat_r/k_r-1|<=epsilon_r. For a nonnegative
physical event flux w_r=k_r d_r(n),

|what_r-w_r|<=epsilon_r w_r.

With stoichiometric vectors nu_r,

|Fhat_i-F_i| <= sum_r |nu_ir| epsilon_r w_r.

Use the corresponding positive-channel decomposition for thermal power,
including fixed binding energies and separately tabulated kinetic-cooling
coefficients. Forward and reverse events remain separate positive quantities
before their net sum. A small cancelling net can have a much larger relative
change than its component coefficient errors.

If ell^T nu_r=0 for every channel, replacing k_r by khat_r preserves the
linear invariant algebraically. Energy transfer must reuse the same event
extent in paired thermal/chemical/escape entries. This preserves the ledger
construction; trajectory accuracy additionally needs dynamical error control.

Let F be the original source, Fhat the accelerated one, y the original IVP
solution and yhat an accelerated reconstruction. Set r=yhat'-F(yhat) and
e=y-yhat. Then e'=F(y)-F(yhat)-r. Residual r contains both Fhat-F and the
numerical solver defect. With a state-tube logarithmic-norm bound a(t) and
residual envelope d(t)>=||r(t)||, finite-time comparison gives

||e(t)|| <= exp(int_s^t a) ||e(s)||
          +int_s^t exp(int_v^t a) d(v) dv.

The inherited RUN16–RUN18 gas/depth block comparison accounts for optical-depth
memory and photo feedback. This table perturbation adds a source forcing
term. A strict contraction hypothesis is unnecessary; actual tube/source
bounds are required for the continuous IVP enclosure.

A prepared bundle is reusable at its exact recorded EOS T and selected
evaluator/model identity. Deliberate stale-temperature reuse adds an error
bounded on one smooth branch by exp(M1 |Delta ln T|)-1. The requested
duplicate-call removal needs no such new approximation. Electron/density/
geometry factors are evaluated from the actual state.

## 7. Additional element selection and source contract

The repository inventory distinguishes:

- PR150's later Li6/Li7 CI/RR/DR provider: source reuse, with explicit
  elemental-electronic-equality and Voronov/Badnell coefficients.
- R9 unit8's actual photo/Milne/total-RR channels: HI,HeI,HeII,LiI,LiII,LiIII.
- This unit's selected new candidate: three Verner–Ferland RR coefficients
  forming BeII, BeIII and BeIV, as an isolated partial number provider.

Verner & Ferland (1996), ApJS103,467, DOI10.1086/192284, Eq.(4), gives

alpha_RR(T)=a/[sqrt(T/T0)(1+sqrt(T/T0))^(1-b)(1+sqrt(T/T1))^(1+b)].

Actual author Table1 bytes and fixed-column metadata were fetched and hashed.

| Formed ion | Z | Final electrons N | a [cm^3/s] | b | T0 [K] | T1 [K] |
|---|---:|---:|---:|---:|---:|---:|
| BeII | 4 | 3 | 2.338e-11 | 0.4211 | 364.7 | 1.215e7 |
| BeIII | 4 | 2 | 1.317e-10 | 0.6691 | 84.73 | 1.412e7 |
| BeIV | 4 | 1 | 4.290e-10 | 0.7557 | 30 | 1.093e7 |

The label is the formed ion; initial charge=Z-N+1, final charge=Z-N.
The low-Z range is 3–10^9 K. Convert cm^3/s by 10^-6 and multiply by
SI n_e n_initial. This is total RR to all final bound levels. It has no
electron-energy gate and supplies no BeI-forming rate, CI, DR, photo transfer,
binding-energy data or thermal-energy moment.

At 10^4 K the newly computed values [cm^3/s] are:

- BeII: 1.4865128496573642e-12.
- BeIII: 5.118059016664173e-12.
- BeIV: 1.0826026237647772e-11.

For -1<=b<=1,

D^2 ln alpha =
-[(1-b)r0/(1+r0)^2+(1+b)r1/(1+r1)^2]/4,

rj=sqrt(T/Tj), so |D^2 ln alpha|<=1/8. This interpolation property is
distinct from atomic-fit accuracy. Our six Li/Be numerical reference rows
cross-check data parsing; Li is not counted as newly developed physics.

No explicit software/data licence was present in the downloaded author
index or table metadata. The implementation is newly written from the cited
formula and numerical data; this receipt does not assign an upstream MIT
licence. Copied PR150 code retains its original licence and provenance.
Badnell's maintained RR data offer a later named alternative. Their N is
initial electrons, unlike Verner's final-electron N, and low-charge fits may
replace B by B+C exp(-T2/T). Adopting them requires provider identity and
a compatibility comparison.

## 8. References, execution and next node

Primary sources actually read:

1. Frozen REI files and C8/C9 reports recorded in SOURCE_AND_RESEARCH_RECEIPT.json.
2. Grackle3.4.1 rate-function documentation:
   https://grackle.readthedocs.io/en/grackle-3.4.1/RateFunctions.html .
3. Verner–Ferland paper:
   https://arxiv.org/pdf/astro-ph/9509083 , printed pp.4–5, Eq.(4);
   author data https://www.pa.uky.edu/~verner/rec.html and
   https://www.pa.uky.edu/~verner/dima/rec/table1.dat .
4. Badnell author metadata:
   https://amdpp.phys.strath.ac.uk/tamoc/DATA/RR/ .

SciSpace provided the primary-paper survey; Exa retrieved author pages and
paper content; Wolfram checked four curvature identities, cubic moments,
the kernel constant and Bell4 identity. WOLFRAM_IDENTITY_RECEIPT.json
preserves its actual outputs, including symbol-name warnings in the first
call followed by zero for all four identities.

Reproduction, where SOURCE_ROOT is the restored native source directory:

python3 analytic_rate_curvature.py --source-root SOURCE_ROOT --output fresh01.json

python3 cubic_rate_bound.py --source-root SOURCE_ROOT --output fresh02.json

python3 -m unittest -v test_rate_math.py

The next current-node implementation is root's paired prepared/table native
consumer and cubic accuracy/performance pilot. Its actual branch, positivity,
ledger and evaluator-identity checks connect these bounds with code.
The open scientific subnode remains continuous floating source/residual
control with gas-opacity feedback within P4-S4C-SPECTRAL-EDGE-SUPPORT.
The original 45/26-node programme retains spectral, angular, birth-time,
donor-domain, full-EoR, Einstein, FLRW-CONV, BI-SIGNED, ISO-COUPLE and nuclear
obligations.

