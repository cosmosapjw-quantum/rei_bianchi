# R2C-R1B forcing-identifiability no-go

## Scope of the result

This is an identifiability result for the currently locked data.  It is not a
no-go theorem for physical photon-conserving histories, and it is not a
numerical-convergence result.  The result assumes only the durable endpoint
node/group lifts, macro/global endpoint moments, and global interval photon
ledger inherited by R2C-R1B.

The local homogeneous audit uses the project conventions
`metric=(-,+,+,+)`, `epsilon_123=+1`, and explicit `c`, `hbar`, and `k_B`.
The spacetime metric is inactive in the local chemistry proof.

## Correct material-state and photon-ledger equations

Let

\[
N(t)=N_{\rm HI}(t),\qquad I(t)=N_{\rm HII}(t),\qquad M=N+I,
\]

with group photoionization currents `J_g >= 0`, collisional ionization event
rate `Q_coll >= 0`, recombination event rate `R_rec >= 0`, and neutral-H
transfer terms `S_{N,+},S_{N,-} >= 0`.  Then

\[
\dot N=-\sum_gJ_g-Q_{\rm coll}+R_{\rm rec}+S_{N,+}-S_{N,-}.
\]

Hence the exact cumulative neutral-H ledger is

\[
\boxed{
\sum_g\int_{t_0}^{t_1}J_g\,dt
=N(t_0)-N(t_1)-\int Q_{\rm coll}\,dt+\int R_{\rm rec}\,dt
+\int S_{N,+}\,dt-\int S_{N,-}\,dt .
}
\]

The quantity on the left has units `cMpc^-3`; `J_g` has units
`s^-1 cMpc^-3`.  This relation constrains an integrated absorbed-photon
budget.  It does not, by itself, identify the time profile or its node/group
partition.

For nonnegative local rates

\[
u(t)=\sum_g\Gamma_g(t)+\beta_{\rm HI}[T(t)]n_e(t),\qquad
r(t)=\alpha_B[T(t)]n_e(t),
\]

the transfer-free H chemistry is

\[
\frac{d}{dt}\begin{pmatrix}N\\I\end{pmatrix}
=
\begin{pmatrix}-u&r\\u&-r\end{pmatrix}
\begin{pmatrix}N\\I\end{pmatrix}.
\]

The generator is Metzler, its column sums vanish, and the boundary vector
field points inward.  Therefore `N>=0`, `I>=0`, and `N+I=M` are preserved.
This proves positivity of a specified forcing operator; it does not supply
that forcing.

## Theorem 1: endpoint-plus-integral temporal non-identifiability

Let `J_*(t)>0` be any admissible current on `[0,T]` satisfying fixed endpoints
and one fixed interval integral.  Set `s=t/T` and

\[
g(s)=s(1-s)\left(s-\frac12\right).
\]

Then

\[
g(0)=g(1)=0,\qquad \int_0^1g(s)\,ds=0.
\]

For sufficiently small nonzero `epsilon`,

\[
J_\pm(t)=J_*(t)\pm\epsilon g(t/T)
\]

remain nonnegative, have the same two endpoints, and have exactly the same
integrated photon count.  They are distinct in the interior.  Therefore the
endpoint-plus-integral map is non-injective.

On a `K`-knot representation, the endpoint values and one quadrature sum have
rank three and nullity

\[
K-3.
\]

For `K=8`, the exact Wolfram and SymPy checks give rank/nullity `(3,5)`.

The durable numerical witness uses an actual R2B G1 node in interval zero.
Both perturbed currents remain positive, preserve endpoints exactly, and
preserve the integral to `1.30e-16` relative residual while their interior
separation reaches `0.3991` relative to the baseline.

## Theorem 2: node-partition non-identifiability even with a pointwise macro total

Consider two positive node currents with fixed endpoints.  Let

\[
f(s)=s(1-s),\qquad f(0)=f(1)=0,
\]

and define

\[
J_1'(t)=J_1(t)+\epsilon f(t/T),\qquad
J_2'(t)=J_2(t)-\epsilon f(t/T).
\]

For sufficiently small `epsilon`, both remain positive and

\[
J_1'(t)+J_2'(t)=J_1(t)+J_2(t)
\]

at every time.  All node endpoints and the pointwise macro/group total are
unchanged, but

\[
\int J_1' dt-\int J_1dt=+\epsilon T/6,
\qquad
\int J_2' dt-\int J_2dt=-\epsilon T/6.
\]

Thus even an exactly known macro/group current history does not determine the
node histories without an independently locked allocation/geometry law.

For `N` nodes and `K` time knots, fixing every node endpoint and the pointwise
macro total gives rank

\[
2N+K-2
\]

and nullity

\[
NK-(2N+K-2)=(N-1)(K-2).
\]

At the project resolution `N=46080`, `K=8`, this is `276474` unconstrained
directions per group and shape/case.  The actual two-node witness preserves
the pointwise total to `1.51e-16` and moves
`4.487443289013829e61 cMpc^-3` of integrated absorbed-photon count from one
node to the other.

## Canonical-data application

The global B2C2A-R1 ledger provides interval-averaged absorption by group.
The R2A sink current accounts for only `0.43616--0.54641` of the global
G1+G2a absorption.  No canonical operator in the locked inputs partitions the
remaining global history into the sink, then into macros, and then into
nodes.

At the macro level the three R2A shape lanes have nearly identical current
sums, but at fixed macro/group total their R2B node distributions differ:
node-level pairwise total variation ranges from `0.006316` to `0.330056`, with
median `0.053431`.  These are admissible endpoint priors, not a unique physical
transport trajectory.

The R2B implementation itself states that it distributes locked R2A moments.
It computes

\[
\Phi_g=J_g^{\rm macro}/\kappa_g^{\rm macro},\qquad
\kappa_{ig}=J_{ig}/\Phi_g.
\]

Consequently `J_{ig}=kappa_{ig} Phi_g` closes at the endpoint by construction
(the maximum durable residual is `9.14346e-16`).  It is not an independent
constitutive law

\[
\kappa_{ig}(t)=\mathcal K_g[N_{\rm HI,i}(t),T_i(t),\text{geometry},\ldots]
\]

needed to iterate a time-averaged optical depth with chemistry.

## Thermal non-identifiability

The primary source prior `phi(E) proportional to E^-2.5` is genuinely present,
so it is incorrect to claim that no spectral information exists.  However,
the energy deposited per absorbed photon depends on the absorbed spectrum,
not only on the group count.  For atomic HI,

\[
\langle E-E_{\rm HI}\rangle_N=
\frac{\int dE\,\phi(E)[1-e^{-\sigma(E)N}](E-E_{\rm HI})}
{\int dE\,\phi(E)[1-e^{-\sigma(E)N}]}.
\]

The optically thin limit is cross-section weighted; the thick limit is
number weighted.  The locked primary auditor gives:

| group | thin excess [eV] | thick excess [eV] |
|---|---:|---:|
| G1 | 2.924008 | 4.164175 |
| G2a | 15.498762 | 16.990432 |
| G2b | 31.261853 | 32.369498 |
| G3 operator auditor | 52.270787 | 57.945669 |

G3 has exactly zero primary source occupation and is not promoted.  Applying
the thin/thick HI auditor to the inherited global photon counts changes the
total photoheating estimate by `14.75--18.60%` across the five intervals.
This does not define the production heating law; it demonstrates that the
missing dynamic optical-depth history is load bearing for temperature.

The 80-digit Precise Special Functions audit independently gives

\[
\frac{\Gamma(4)\zeta(4)}{\Gamma(3)\zeta(3)}
=2.701178032919063896\ldots,
\]

which is the blackbody mean photon energy in units of `k_B T`.  It is retained
only as a limiting check that photon-number and energy moments are distinct,
not as the production ionizing spectrum.

## Conclusion

The inherited constraints prove endpoint admissibility and global photon
bookkeeping.  They do not identify:

1. a time-resolved incident or absorbed group forcing;
2. a canonical global-to-sink-to-macro-to-node partition;
3. a node dynamic-opacity law independent of endpoint `J/Phi` construction;
4. the evolving absorbed-energy moment and genuine thermal operator.

Therefore R2C-R1B must fail closed on identifiability before a production
fixed-point integration is attempted.
