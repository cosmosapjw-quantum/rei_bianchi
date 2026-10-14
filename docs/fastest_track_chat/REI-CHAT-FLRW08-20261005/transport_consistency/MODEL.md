# Projected pure transport: all-state real-arithmetic bound

Same task: `REI-CHAT-FLRW08_PAIRED_TIME_ERROR_CONTROL`. Original parent:
`e63ca0735a3e3e7eebbf4498c697d806d375e191`. This unit proves an auxiliary
finite-grid pure-transport statement and binds its formulas to a finite sample
of the original native transport prefix. No chemistry, source, coupled history,
full campaign, physical admission, or floating-point enclosure is established.
Scientific admission stays **HOLD**.

## Hypotheses and domain

Fix strictly increasing positive energy nodes E0,...,E32, with E0=10 eV.
Here these are the original m8 nodes between edges
10,13.598434599702,13.6,13.7,20 eV. The exact rational diagnostics interpret
the stored binary64 nodes as exact real numbers. Photon coordinates are
photons/H, guardN is photons/H, guardU is eV/H, and time is proper seconds.
Use the original piecewise linear nodal hats, and let M_r transport each
population from E_j to r E_j, 0<r<=1. Below E0 the entire population goes
to guardN and its transported energy to guardU; existing guardN stays fixed
and existing guardU is multiplied by r. This is an algebraic pure-transport
map, including its closed nonnegative cone 0<=guardU<=E0 guardN.

P sets p0 to zero and adds p0 to guardN and E0*p0 to guardU. It preserves
number and energy. The original public `validate` requires guardU<E0 guardN
for positive guards. P can attain equality, e.g. occupied E0 with initially
empty guard. **P is auxiliary on the closure; P M_r P is not asserted to be
a callable public `paired_trial` on every intermediate state.** Native inputs
in this unit satisfy the original strict condition before extraction calls.

Reduced number coordinates are p1,...,p32,guardN. Reduced energy coordinates
are p1,...,p32,guardU. These two linear maps share the spectrum but carry
different guard quantities; they are not two independent physical spectra.
All-state operator bounds also apply to signed differences of physical states.

## Projection identity, including the lowest-node discontinuity

In real arithmetic, P M_r = P M_r P for every 0<r<=1.
Proof: P changes only the E0 column. For r<1, M_r sends that column to
guardN=1,guardU=r E0. Applying P first gives guardN=1,guardU=E0,
which M_r transforms to exactly the same pair. For r=1, M_1 is the identity
and P^2=P. All other columns are unchanged. Linearity completes the proof.
For every finite composition, one can insert P between transport maps and
at the initial state without changing the final projected output:

`P M_rn ... M_r1 = (P M_rn P) ... (P M_r1 P)`.

The raw maps may leave a transient p0 before the next step; this identity
includes that transient. It does not remove the full-state discontinuity of
M_r as r approaches1 from below at occupied E0. The unprojected full-domain
finite generator still does not exist there. Neither this identity nor finite
native samples prove a chemistry/source composition identity.

## CFL generators and exact characteristic semigroups

Define lambda_j=E_j/(E_j-E_(j-1)), Lambda=max lambda_j, and x=1-r.
In each spectrum column j, B has diagonal -lambda_j and downward
+lambda_j; j=1 goes to guardN instead of p0. The guardN column is zero.
C has the same spectrum entries, but j=1 sends E0*lambda_1 to guardU,
and its guardU diagonal is -1. No other entries occur.

If x Lambda<=1, r E_j lies between E_(j-1) and E_j for every j>=1.
The original hats therefore place 1-x lambda_j at E_j and x lambda_j
at E_(j-1). P sends any E0 hat contribution directly to the guards.
Consequently the **actual projected hat maps** satisfy

`K_N(r)=I+x B`, `K_U(r)=I+x C`.

Outside this CFL domain the original hat maps remain defined, positive, and
moment-preserving, but these linear expressions generally fail and can be
negative. `cfl_linear_map` explicitly rejects non-CFL arguments; the required
`projected_*_map` APIs always compute the actual hats, including non-CFL r.

For a fixed q ray and constant nonnegative directional H_i,
g(t)^2=sum_i q_i^2 exp(-2H_i t). Then
H_d(t)=-d log(g)/dt is the positive weighted mean of the H_i.
The dimensionless characteristic increment is
s=-log(r)=integral H_d dt. The reduced transport ODE is
z'=H_d(t) B z for number, or z'=H_d(t) C z for energy.
Since each generator is fixed, its exact evolution is exp(s B) or exp(s C).
For the actual geometries H_i>0, positive endpoint dt gives 0<r<1.

## Norms, conservation, and positivity

The number norm is ordinary l1. The energy norm is weighted l1 with
w=(E1,...,E32,1): ||z||_w=sum E_j |p_j|+|guardU|.
Induced l1 norms are the maximum absolute column sum; in the weighted norm
one applies the same rule to diag(w) A diag(w)^(-1).
Thus ||B||_1=2 Lambda. Each spectrum column of C has absolute weighted
column sum lambda_j+lambda_j*E_(j-1)/E_j=2 lambda_j-1; its guard
column has norm1. Since lambda_j>1, ||C||_w=2 Lambda-1.

B,C are Metzler. B's column sums are zero, and w^T C=-w^T. Their
exponentials are positive; exp(sB) has norm1 and exp(sC) has weighted
norm exp(-s). In the CFL domain K_N is positive and column-stochastic,
while K_U is positive with w^T K_U=r w^T. The same positivity and moments
hold for the actual non-CFL hats by their partition of unity and linear
energy reproduction, including the below-grid guard branch.

In particular, **total photon energy including guard is exactly r times
the old total** in each original hat map and in the exact characteristic
semigroup. Number is conserved. Equality of total energy does not imply
equality of spectra, absorption, gas evolution, or a coupled error bound.

## Real-arithmetic local and composition bounds

For A=B or C in its specified norm, put L=||A||. The contractive semigroup
gives the integral remainder identity

`exp(sA)=I+sA+integral_0^s (s-u) A^2 exp(uA) du`.

Since x=1-exp(-s)<=s, subtracting from I+xA and taking norms yields

`||K(r)-exp(sA)|| <= L*(s-(1-exp(-s))) + (L^2*s^2)/2 = delta(L,s)`.

This bound assumes each discrete step is CFL. For any finite partition,
telescoping the products and using contractivity on both sides gives

`||K_n...K_1-exp((sum s_k)A)|| <= sum delta(L,s_k)`.

The number difference is also <=2, so the number bound can be clipped at2.
Energy can likewise be clipped at2 (indeed at2 exp(-sum s_k)). Multiplying
the operator bound by the initial norm gives an absolute state bound.
These statements quantify all states, rather than only the initial probe.

As s-(1-exp(-s))<=s^2/2 and sum s_k^2<=s_max*sum s_k,
an explicitly computable coarse bound is
`(L+L^2)*s_max*s_total/2`. This involves no trajectory execution.
For max endpoint step dt, s_max<=Hmax*dt. Because H_d is a weighted mean,
x<=s<=Hmax*dt, and the uniform sufficient CFL condition is

`dt <= 1/(Hmax*Lambda)`.

For the stored grid Lambda=69502.98919618955, with exact rational value
2552039788843281/36718417702. The BI sufficient endpoint maximum is
1424541622.3843098 seconds. The original macro minimum1000 corresponds
to half endpoint500; no original step policy is changed here.
RESULTS tabulates finite representative rays, endpoint500/1000/6.25e8/1.25e9,
and total windows1e10/1e13. The direction-independent coarse number bound
for Hmax=1.01e-14, window1e13, endpoint500 is about .00492780 times
initial number; actual representative-ray bounds are at most .00492338.
The large-step bounds saturate at2 and are loose, not useful coupled
certificates. The characteristic variation has been bounded analytically;
billions of minimum-size steps were not executed to make this table.

## Native binding and floating-point scope

`run_analysis.py` compiles the exact current lib.rs using rustc1.94.1 and
mechanically copies all definitions before `fn endpoint`. It copies the
original endpoint body from its opening brace to just before
`let (weights,wb)=source_weights(c,h,t1)?;` verbatim, changes its wrapper
name/return signature, and appends only return, chosen-ratio, and input
validation helpers. Original prefix lines181..223, body bytes13526..16466,
body SHA256 2ccf27b5ebd0ecf1be614aa038e0673701e4b1ad7683f8936e6b65cf6552b82b
are recorded along with generated module/source/binary hashes and argv.
The copied module contains unused source/chemistry helper definitions; the
executed wrapper never calls source injection or chemistry. It is an
**original-prefix wrapper, not the original full endpoint**.

One native process executed2240 cases: all33 nodal bases, guard-only,
dense with preexisting guard; two geometries; times0/5e12; original rays
0/17/63/127; dt1000/6.25e8/1.25e9/2e9. There are560 non-CFL cases.
Nodal basis1 is used except occupied E0=.05; all input interval boxes are
exact binary points, and the original input validator is called. Only
chosen-ray point spectra and guards are stored, not full-state dumps.
Maximum normalized native-vs-hat error is6.6964e-18, and total-energy
relative residual is2.5213e-16. Comparisons divide number l1 differences
by input number and weighted-energy l1 differences by input energy and
take their maximum, with the frozen1e-9 threshold. Raw residuals are retained.

Finite basis column tests quantify numerical matrix operators; the written
proof supplies the real-arithmetic universal statement. There is **no
floating-point rigorous envelope**. Thin grid spacing amplifies arithmetic
error: at s=5e-12 the numerical matrix/expm defect is8.87e-12 while the
real-arithmetic bound is2.42e-13. This explicitly exceeds the bound when
interpreted as a statement about binary64 implementations. The table records
it unchanged. The larger four steps used by the frozen oracle satisfy its
numerical slack and the real bound; this is numerical evidence, not validated
roundoff containment. Native agreement also cannot remove shared arithmetic
error. Interval computations inside the original prefix do not certify the
entire numerical semigroup/composition comparison.

## Conditional coupled stability requirements

For a coupled certificate, fix the **same** reduced model and norm, establish
a forward-invariant domain D containing the exact and numerical states,
and certify all chemistry/temperature/provider and guard domains there.
The auxiliary closure must be reconciled with the public strict guard domain;
transport projection alone does not establish public runtime admissibility.
Establish existence/uniqueness and bounds on the derivatives needed for the
chosen local error order of chemistry, radiation sinks, source weights,
geometry, and the stage solver. Bound coupling and splitting terms, including
relevant Jacobian products/commutators and time derivatives. Certify numerical
stage residual/enclosure and roundoff contributions, rather than assuming
that transport moment conservation bounds them.

Precisely, if the complete endpoint map Psi_k is Lipschitz on that domain
with factor a_k and has a certified defect eta_k against the exact coupled
flow from every relevant input, the conditional recurrence is

`e_(k+1)<=a_k e_k+eta_k`,
`e_n<=prod a_k*e_0+sum_j eta_j*prod_(k>j) a_k`.

For certified a_k<=exp(L_D dt_k) with L_D>=0, this implies the corresponding
Gronwall bound <=exp(L_D T)*(e_0+sum eta_k). A one-sided/contraction estimate could
improve it only if established in the selected norm and domain. A bound on
the exact flow alone does not automatically bound the numerical Psi_k.
Transport delta is one component of eta_k, not the complete eta_k.
**D, L_D, a_k, chemistry/source consistency constants and certified eta_k
are not established in this unit.** No numerical constants are invented and
no small-signal or global coupled contraction/certificate is claimed.
