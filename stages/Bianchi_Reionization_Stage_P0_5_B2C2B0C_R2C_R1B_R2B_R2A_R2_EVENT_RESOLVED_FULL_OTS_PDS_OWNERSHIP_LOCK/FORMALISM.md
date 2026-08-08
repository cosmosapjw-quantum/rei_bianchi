# Event-resolved full-OTS formalism

## 1. Conventions and species state

Metric signature is `(-,+,+,+)`, `epsilon_123=+1`, and `c`, `hbar`, `k_B` remain explicit. The material population vector is

\[
\mathbf N=(N_{\rm HI},N_{\rm HII},N_{\rm HeI},N_{\rm HeII},N_{\rm HeIII})^T.
\]

Elementary ionization stoichiometries are

\[
\mathbf s_H=(-1,+1,0,0,0)^T,
\]
\[
\mathbf s_{\rm HeI}=(0,0,-1,+1,0)^T,
\]
\[
\mathbf s_{\rm HeII}=(0,0,0,-1,+1)^T.
\]

The invariant covectors

\[
\mathbf c_H=(1,1,0,0,0)^T,
\qquad
\mathbf c_{\rm He}=(0,0,1,1,1)^T
\]

obey `c_H.s_e=c_He.s_e=0` for every material event.

## 2. Source-conditioned event graph

Let `R_alpha >= 0` be a parent-channel rate. The event-resolved population source is

\[
\dot{\mathbf N}=\sum_e \mathbf s_e\,\Phi_e,
\qquad \Phi_e=R_{\alpha(e)}b_e\ge0,
\]

where `b_e` is the source branch multiplicity. The full-OTS parent and child events are:

- H II case B: `-s_H`;
- He II ground: `-s_HeI + y s_H + (1-y)s_HeI`;
- He II case B: `-s_HeI + p s_H` plus nonionizing remainder `1-p`;
- He III ground: `-s_HeII +(1-y2a-y2b)s_H+y2b s_HeI+y2a s_HeII`;
- He III `n=2`: `-s_HeII+s_H`;
- He III cascade:
  \[
  -\mathbf s_{\rm HeII}+A_H\mathbf s_H+A_{\rm HeI}\mathbf s_{\rm HeI},
  \]
  with
  \[
  w=(\ell-m)+my,
  \]
  \[
  A_H=vw+(1-v)fz,
  \qquad
  A_{\rm HeI}=vm(1-y)+(1-v)f(1-z).
  \]

Here

\[
p=\frac{24}{25},\qquad \ell=\frac{57}{40},\qquad m=\frac{737}{1000}.
\]

## 3. Conditional uniqueness theorem

**Theorem.** Given (i) the named source parent channels, (ii) the elementary stoichiometric set above, (iii) the source branch functions `y,z,y2a,y2b,v,f`, and (iv) typed nonionizing and escape ledgers, the expected event multiplicities in `EVENT_REGISTRY.csv` uniquely reproduce the source population operator. The net RHS without (i)–(iv) is not sufficient.

**Proof sketch.** Each parent removes exactly one ion from a source-defined charge state. Each emitted packet is partitioned over the source-listed absorbers and a typed remainder. The branch partitions sum exactly, and the allowed child stoichiometries are linearly independent once the parent and packet class are fixed. The symbolic residual of each reconstructed vector is zero. Zero-stoichiometry radiative remainders are fixed by photon-count completion, not by the population RHS.

This is conditional uniqueness of an *expected event graph*, not a claim that individual cascade photon energies or directions are identified.

## 4. Branch positivity and photon counts

For

\[
0\le y,z,v,f\le1,
\qquad y_2^a,y_2^b\ge0,
\qquad y_2^a+y_2^b\le1,
\]

all event multiplicities are nonnegative. Further,

\[
w+m(1-y)=\ell,
\]

so the two-photon branch has `ell` expected ionizing packets and `2-ell` nonionizing packets. The Ly-alpha branch has absorbed count `f` and escaped count `1-f`. The expected number of emitted photons in the mixed cascade is

\[
2v+(1-v)=1+v.
\]

## 5. Augmented energy conservation

Define chemical binding energy relative to neutral ground states,

\[
E_{\rm chem}=\chi_H N_{\rm HII}
 +\chi_{\rm HeI}N_{\rm HeII}
 +(\chi_{\rm HeI}+\chi_{\rm HeII})N_{\rm HeIII}.
\]

For absorption of a packet of energy `epsilon` by a threshold `chi`,

\[
\Delta E_\gamma=-\epsilon,
\quad \Delta E_{\rm chem}=+\chi,
\quad \Delta U_{\rm res}=\eta(\epsilon-\chi),
\quad \Delta E_{\rm OTS}^{\rm unres}=(1-\eta)(\epsilon-\chi),
\]

and therefore

\[
\Delta E_\gamma+\Delta E_{\rm chem}
 +\Delta U_{\rm res}+\Delta E_{\rm OTS}^{\rm unres}=0.
\]

For recombination with electron kinetic-energy loss `kappa`,

\[
\Delta E_{\rm chem}=-\chi,
\qquad \Delta U_{\rm res}=-\kappa,
\qquad \Delta E_\gamma=\chi+\kappa,
\]

which also sums to zero. Until the OTS packet spectrum is source-locked, set no unknown excess energy to zero: keep it in `E_OTS^unres`.

## 6. Production–destruction representation

With event fluxes, the PDS tensor is no longer inferred from a net vector. For `i != j`,

\[
P_{ij}=\sum_{e:j\to i}\Phi_e,
\qquad D_{ji}=P_{ij},
\]

and

\[
\dot N_i=\sum_{j\ne i}(P_{ij}-D_{ij}).
\]

This representation is nonnegative and preserves H and He nuclei exactly. MPRK22 can consume these source-defined event fluxes without changing its accepted coefficients.
