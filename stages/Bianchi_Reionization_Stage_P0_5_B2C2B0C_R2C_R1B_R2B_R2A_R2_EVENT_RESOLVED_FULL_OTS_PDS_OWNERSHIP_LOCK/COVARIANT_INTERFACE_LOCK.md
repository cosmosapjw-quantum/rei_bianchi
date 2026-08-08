# Covariant Bianchi and CMB interface lock

This document closes interfaces needed later; it does not implement Bianchi feedback or CAMB transfer.

## 1. Hydrogen-frame thermal equation

Use a unit timelike hydrogen-frame velocity `u_H^a u^H_a=-1` and

\[
T^{ab}=\rho u^a u^b+p h^{ab}+2u^{(a}q^{b)}+\pi^{ab}.
\]

If `nabla_b T^{ab}=Q^a`, the 1+3 energy projection is

\[
\dot\rho+(\rho+p)\Theta_H+D_aq^a+2A_aq^a+\sigma_{ab}\pi^{ab}
=-u_aQ^a.
\]

In the isotropic local gas frame (`q^a=0=pi^{ab}`), for parcel volume `V` with `D_0V=Theta_H V`,

\[
D_0U+p\Theta_HV=\dot Q_{\rm res}-\Lambda
 +W_{\rm mass}+W_{\rm unresolved\ exchange}.
\]

The current `3HpV` term is only the FLRW/comoving specialization `Theta_H=3H`. Finite tilt and general Bianchi evolution must supply the actual hydrogen-frame expansion scalar.

## 2. Event four-force boundary

For event rate `Phi_e` and mean tetrad momentum transfer `Delta p_e^{hat a}`,

\[
G_{\rm event}^{\hat a}=\sum_e\Phi_e\langle\Delta p_e^{\hat a}\rangle.
\]

The scalar full-OTS source locks the time component only after its packet energy moment is known. It does not identify directional momentum. An isotropic OTS spatial source may be used only after an explicit isotropy assumption is registered; otherwise the spatial four-force remains unresolved.

## 3. Thomson optical-depth interface

The electron density owned by reionization chemistry is

\[
n_e=n_{\rm HII}+n_{\rm HeII}+2n_{\rm HeIII}.
\]

For physical electron four-velocity `U_e^a U^e_a=-c^2`, unit velocity `u_e^a=U_e^a/c`, and null tangent `k^a=dx^a/dlambda`,

\[
\frac{d\tau}{d\lambda}=n_e\sigma_T(-u_{ea}k^a)
=n_e\sigma_T\frac{-U_{ea}k^a}{c}.
\]

For conformal time in seconds in FLRW,

\[
\frac{d\tau}{d\eta}=a n_e\sigma_T c.
\]

If the independent conformal coordinate is a length rather than a time, the final factor `c` is omitted. This unit distinction must be encoded in the future adapter.

## 4. Recombination splice firewall

`rec_bianchi` and `rei_bianchi` may exchange typed snapshots only after a deliberate adapter review. A valid splice must specify one owner for each atomic/radiative term, continuity or controlled transition of `n_e` and `T_m`, and a no-double-count matrix for photon and thermal sources. No numerical recombination state or rate is imported in this stage.
