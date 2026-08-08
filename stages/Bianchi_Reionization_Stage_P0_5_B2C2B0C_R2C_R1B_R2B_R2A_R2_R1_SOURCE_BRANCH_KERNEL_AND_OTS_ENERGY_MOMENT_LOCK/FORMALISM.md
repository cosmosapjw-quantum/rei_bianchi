# Source branch kernel and OTS energy-moment formalism

## 1. Scope and conventions

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B` remain explicit.  The background is homogeneous; tetrad and 1+3 interfaces are inherited.  This stage changes no MPRK22(1), Alexander-SDIRK2, owner law, material state or ten-ledger equation.

The inherited He III cascade branch is

\[
A_H=v[(\ell-m)+my]+(1-v)fz,
\]
\[
A_{\rm HeI}=vm(1-y)+(1-v)f(1-z),
\]
with
\[
\ell=\frac{57}{40}=1.425,\qquad m=\frac{737}{1000}=0.737.
\]
Here `y` splits two-photon packets above the He I threshold between H I and He I, `z` splits He II Ly-alpha absorption, `v` is the two-photon branch, and `f` is the absorbed Ly-alpha fraction.

## 2. Hummer--Seaton nodal branch table

Hummer & Seaton write the He II Ly-alpha branch with coefficient `1-X(He+)` and the two-photon branch with coefficient `X(He+)`.  Their Table V tabulates `2[1-X(He+)]`.  Hence the source nodal two-photon fraction is

\[
\boxed{v=X=1-\frac12\,\{2(1-X)\}}.
\]

The recovered nodal values are

\[
\begin{array}{c|ccccc}
\log_{10}(T/{\rm K})&4.00&4.25&4.50&4.75&5.00\\ \hline
v&0.285&0.305&0.325&0.350&0.375
\end{array}
\]

These five values are source-identical.  The historical sources say that the table was interpolated but do not identify the interpolation algorithm.  Therefore:

- the table nodes are load bearing;
- a linear interpolation in tabulated `log10 T` is a named adapter, not source identity;
- no extrapolation below `10^4 K` or above `10^5 K` is permitted;
- outside the table domain the only source-safe probability interval is `0<=v<=1`.

For an interior table cell, the stage also records the convex cell interval

\[
\min(v_r,v_{r+1})\le v\le\max(v_r,v_{r+1})
\]

as a declared shape-preserving adapter envelope.  This is narrower than the strict source-safe probability interval and must remain labeled as an adapter assumption.

## 3. The Ly-alpha absorption fraction

The full-OTS equations use `f` as the fraction of He II Ly-alpha photons absorbed locally and `1-f` as the escaped fraction.  The cited source supplies only

\[
\boxed{0.1\le f\le1},
\]

with dependence on neutral fraction stated qualitatively.  No executable `f(x_{\rm HI})` is source identified.  The previous exponential law is therefore an auditor only.

## 4. Multi-affine corner theorem

For fixed `y,z`, each branch multiplicity is multi-affine in `(v,f)`.  In particular,

\[
\frac{\partial^2 A_H}{\partial v\,\partial f}=-z,
\qquad
\frac{\partial^2 A_{\rm HeI}}{\partial v\,\partial f}=-(1-z).
\]

**Theorem.** Let `R=[v_-,v_+]x[f_-,f_+]`.  Every multi-affine scalar function on `R` attains its minimum and maximum at a vertex of `R`.

**Proof.** Holding `f` fixed makes the function affine in `v`, so its extrema lie at `v=v_-` or `v=v_+`.  Restricting to either edge makes it affine in `f`, whose extrema lie at `f=f_-` or `f=f_+`.  Thus only the four vertices are required. `QED`.

Consequently every node is audited with exactly four predeclared corners.  No post-hoc corner selection is allowed.

The full emitted-photon identity is

\[
A_H+A_{\rm HeI}+v(2-\ell)+(1-v)(1-f)=1+v.
\]

All terms are nonnegative for `0<=v,f,y,z<=1` because

\[
\ell-m=\frac{86}{125}>0,\quad m>0,\quad 2-\ell=\frac{23}{40}>0.
\]

## 5. Canonical-domain audit

For the 46,080-node `z=6` material state,

\[
2096.739\ {\rm K}\le T\le66266.847\ {\rm K}.
\]

The node counts are

\[
N(T<10^4\,{\rm K})=21600,
\]
\[
N(10^4\,{\rm K}\le T\le10^5\,{\rm K})=24480,
\]
\[
N(T>10^5\,{\rm K})=0.
\]

Thus 46.875% of the canonical nodes lie below the source table.  Any production use of a single `v(T)` across the full state would require a new source, a declared physical extension, or an uncertainty lane.

The four-corner node audit gives no negative multiplicity and closes the photon identity to

\[
4.45\times10^{-16}.
\]

## 6. Exact He II Ly-alpha first moment

With NIST ionization thresholds

\[
\chi_H=13.598434599702\ {\rm eV},
\]
\[
\chi_{\rm HeI}=24.587389011\ {\rm eV},
\]
\[
\chi_{\rm HeII}=54.417760\ {\rm eV},
\]

the hydrogenic He II Ly-alpha energy is

\[
E_{\rm Ly\alpha}=\frac34\chi_{\rm HeII}=40.813320\ {\rm eV}.
\]

The photoelectron excess energies are therefore exactly

\[
\epsilon_H^{\rm Ly\alpha}=27.214885400298\ {\rm eV},
\]
\[
\epsilon_{\rm HeI}^{\rm Ly\alpha}=16.225930989\ {\rm eV}.
\]

For the adopted H/He-only scalar full-OTS model, these two absorbed branches may own resolved heating.  The escaped branch owns `E_Lyalpha` in the escaped-radiation ledger.

## 7. Two-photon first-moment non-identifiability

The source fixes two zeroth moments per two-photon event:

\[
N(E\ge\chi_H)=\ell=1.425,
\qquad
N(E\ge\chi_{\rm HeI})=m=0.737,
\]

and the pair energy

\[
E_1+E_2=E_{\rm Ly\alpha}.
\]

Let `e=min(E_1,E_2)` and divide symmetric pairs into three support classes:

- A: `0<=e<chi_H`, with counts `(n_H,n_HeI)=(1,1)`;
- B: `chi_H<=e<E_Lyalpha-chi_HeI`, with counts `(2,1)`;
- C: `E_Lyalpha-chi_HeI<e<=E_Lyalpha/2`, with counts `(2,0)`.

The source count constraints determine only the class weights:

\[
a=2-\ell=\frac{23}{40}=0.575,
\]
\[
b=m-a=\frac{81}{500}=0.162,
\]
\[
c=1-a-b=\frac{263}{1000}=0.263.
\]

They do not determine the value of `e` inside any class.

**Theorem.** The data `(ell,m,E_Lyalpha)` do not uniquely determine either the H-capable or He-I-capable first spectral moment.

**Proof.** Choose any admissible `e_A,e_B,e_C` in their respective intervals and place a symmetric pair `(e_r,E_Lyalpha-e_r)` in each class with weights `(a,b,c)`.  Every such measure has two photons, total energy `E_Lyalpha`, H-capable count `a+2b+2c=ell`, and He-I-capable count `a+b=m`.  Varying `e_A` or `e_B` changes the corresponding first moments while preserving all constraints. `QED`.

Two explicit witnesses in `TWO_PHOTON_ENERGY_MOMENT_WITNESS.json` have identical counts and total pair energy but differ by more than `7 eV` in H-capable excess and more than `8 eV` in He-I-capable excess.

The sharp limiting ranges under this support decomposition are

\[
32.9942201052\le M_H^{(1)}\le40.8133200000\ {\rm eV},
\]
\[
13.6164508006\le Q_H^{\rm excess}\le21.4355506954\ {\rm eV},
\]
\[
19.6317161250\le M_{\rm HeI}^{(1)}\le27.8764704348\ {\rm eV},
\]
\[
1.51081042385\le Q_{\rm HeI}^{\rm excess}\le9.75556473374\ {\rm eV}.
\]

These are spectrum-class moments, not a claim that absorber competition is energy independent.  Any resolved heating split additionally requires an energy-conditioned absorption law.

## 8. Other OTS packet classes

The following remain first-moment unresolved:

- He II ground-state free-bound packets;
- He II case-B cascade packets;
- He III ground-state free-bound packets;
- He III `n=2` Balmer-continuum packets;
- He III two-photon packets.

Their photon-number event topology is locked, but unidentified energy remains in `E_OTS^unres`.  It must never be silently set to zero.

## 9. Augmented energy theorem

For absorption of a packet of energy `epsilon` by threshold `chi`, assign

\[
\Delta E_\gamma=-\epsilon,
\quad
\Delta E_{\rm chem}=+\chi,
\]
\[
\Delta U_{\rm res}=\eta(\epsilon-\chi),
\quad
\Delta E_{\rm OTS}^{\rm unres}=(1-\eta)(\epsilon-\chi).
\]

Then

\[
\Delta E_\gamma+\Delta E_{\rm chem}+\Delta U_{\rm res}+\Delta E_{\rm OTS}^{\rm unres}=0
\]

for every `0<=eta<=1`.  Therefore uncertainty in the first moment changes only the split between resolved and unresolved ledgers; it does not break total-energy conservation.

## 10. Claim boundary

This stage identifies:

- the Hummer--Seaton nodal `v` values;
- a finite branch-corner theorem;
- the source interval for `f`;
- exact He II Ly-alpha energy ownership;
- constructive and bounded two-photon first-moment non-identifiability;
- a complete unresolved-energy owner matrix.

It does not identify:

- a source-identical continuous `v(T)`;
- any `v(T)` below `10^4 K`;
- a unique `f(x_HI)`;
- resolved heating for free-bound, Balmer, case-B or two-photon packets;
- directional OTS momentum.

Accordingly it authorizes only bounded branch/energy propagation, not a production history.
