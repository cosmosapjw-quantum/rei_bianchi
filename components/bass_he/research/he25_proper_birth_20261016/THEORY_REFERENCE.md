# HE25 proper-time reference: definitions and numerical lane

## Source and scope

The assigned HE25 construction prescribes an isotropic, truncated 50,000 K
blackbody birth spectrum and a photon source per original hydrogen nucleus
`S_x=dN/d ln(a)`. The physical proper-time source is **`S_t=H(a) S_x`**.
The original native `bass_cr` H/He model owns CI, RR, DR, gas cooling, CMB and
escape terms. The common physical RHS must include those terms. The HE23
`he21_photo.py` is useful for its stated Verner row, spectral and angle
conventions but is a photo-only prior experiment, not the HE25 microphysics.
The LRS metric and the original photon construction are fixed by the parent
HE25 model; this note derives the independent integration and checks its
conservation form. No EoR or upstream equivalence follows from this lane.

## Covariant photon variable and pushforward

Write an axisymmetric LRS line element, with signature `(-,+,+,+)`, as

`ds² = -c²dt² + a_perp(t)²(dx²+dy²) + a_parallel(t)² dz²`.

The spatial covariant momentum components `p_i` are constants because the
spatial coordinate fields are Killing fields. For a photon born at `t_b`, label
its conserved momentum by birth energy `E_b` and direction cosine `mu_b` to
the symmetry axis. Its energy in the comoving orthonormal frame at time `t` is

`E(t) = E_b sqrt[(1-mu_b²)(a_perp,b/a_perp(t))² + mu_b²(a_parallel,b/a_parallel(t))²]`.

For the continuous-birth problem use a *fixed covariant momentum grid* instead.
Let its radial and angular coordinates be `(P,nu)` with `p_perp=P sqrt(1-nu²)`
and `p_parallel=P nu`. Put `A_perp=c/a_perp`, `A_parallel=c/a_parallel`, and
`G(t,nu)=sqrt[A_perp²(1-nu²)+A_parallel² nu²]`. Then
`E=P G` and `mu=nu A_parallel/G`. The source at each proper time is the
pushforward of the isotropic **current birth-frame** law `b(E)dE dmu/2` into
this fixed grid, with Jacobian

`J(t,nu)=|∂(E,mu)/∂(P,nu)|=A_parallel A_perp²/G²`.

Consequently the source density in `(P,nu)` is
`Q(P,nu,t)=H(a) S_x(t) b(PG(t,nu)) J(t,nu)/2` on the truncated spectral
support. Its cell integrals `Q_j(t)` vary with time. A fixed-grid quadrature
must account for moving source-support boundaries; fixing birth weights for
all times would represent a different source history. The photon stock
`P_j(t)` is number per original H nucleus in fixed cell `j`; no transport
remapping is needed. Thus

`dP_j/dt = Q_j(t) - P_j Σ_i λ_ij(t)`, with
`λ_ij = c n_H(t) f_i(t) σ_i(E_j(t)) >= 0`.

Here `f_i` is the number of available absorber nuclei of species `i` per H
nucleus; the model determines its gas-state dependence. `P_j λ_ij` is an
absorption rate per H nucleus. The photon source support and each fit cutoff
are time discontinuities or derivative discontinuities of this RHS. Their
physical crossing times are exact segment boundaries in the solver.

For the HE23 axis convention, `a_perp/a_perp,b = exp(x-b)`,
`a_parallel/a_parallel,b = exp(x+2b)`, `x=ln(a/a_b)`, and `b=-q x`. The above
gives its documented factor
`E/E_b = exp(-x) sqrt[(1-mu_b²)exp(2b)+mu_b²exp(-4b)]`.
The exact LRS scale factors, `q` policy and integration endpoints are supplied
by HE25, rather than inferred from HE23's controlled constant-q experiment.

## Energy and number accounting

Set `A_i(t)=∫Σ_j P_j λ_ij dt`,
`N_src(t)=∫Σ_j Q_j dt`, and `U_src(t)=∫Σ_j E_j Q_j dt`.
Then the physical number identity is

`N_src = Σ_j P_j + Σ_i A_i`, assuming zero initial photons; add initial
photon number on the left otherwise. For photon energy
`U_γ=Σ_j E_j P_j`, define positive or signed metric work by
`dW_γ/dt=-Σ_j P_j dE_j/dt`. It follows directly that

`dU_γ/dt = dU_src/dt - Σ_ij E_j P_j λ_ij - dW_γ/dt`.

An absorption of species `i` adds `E_j-B_i` to gas thermal energy and `B_i`
to binding energy, where `B_i` is its physical ionization threshold. With the
native microphysical channels included, chemical transfers, radiation losses,
gas expansion and CMB exchange require their own explicit signed ledgers.
Transport contributes gas expansion **once**, `-2H u` for a nonrelativistic
monatomic gas energy per original H nucleus; it must not be duplicated by the
native microphysics wrapper. In the transport-only limit, one obtains
`U_src+U_γ(0)+u(0)+B(0)=U_γ+u+B+W_γ+W_g`, with
`dW_g/dt=2H u`. For the full native model this identity additionally includes
the corresponding native radiation/exchange ledgers. A small numerical defect
is evidence about implementation accuracy, not a physical claim by itself.

## Independent numerical formulation

`reference.solve_reference` solves the **same physical proper-time state and
RHS** as the parent HE25 model, but uses SciPy `solve_ivp` with `Radau` (or
`DOP853`) instead of the parent positive Duhamel transport discretization.
For positive coordinate scale `s`, it evolves `z=y/s` and evaluates
`dz/dt=F(t,sz)/s`. This changes conditioning only. Every declared exact
source-support or threshold crossing time starts a new solver segment; the
optional `model.set_interval(left,right)` freezes the active masks so the RHS
has the correct one-sided value at both shared endpoints. Default
`rtol=1e-10`, `atol=1e-12` apply to `z`, not unscaled gas or photon units.
An optional physical Jacobian `J_y=∂F/∂y` is transformed to
`J_z=diag(1/s) J_y diag(s)` and passed to Radau; otherwise optional model
Jacobian sparsity is passed for finite differences. No hidden precision,
source reconstruction, tolerance adjustment or fallback backend is used.

The current small analytic checks cover `S_t=H S_x`, a switched continuous
source with absorption and its number ledger, plus breakpoint validation.

## Bounded HE25 pilot evidence (2026-10-16)

One independent `Radau` endpoint pilot used `Model(m=4,angles=4,q=0)`, 256
fixed photon modes and 20 interior crossing breakpoints. The shared physical
RHS had SHA256
`6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c`;
this reference had SHA256
`55bb8721a72e3e75b126f0198b5cd165eb7250435e863b3ace1378a68b4cbff3`;
the original native owner binary had SHA256
`22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5`
and source commit `f7830e2f55e7a1938bc3c98f61b60651f8dae474`.
The command used `rtol=1e-9`, scaled `atol=1e-11`, and completed in 17.55 s
with 4,608 native point calls. The full endpoint result and fsynced native
call stream are at
`/root/HE25_NCP_BIRTH_20261016/reference_pilot/radau_pilot.json` and
`radau_pilot_raw.jsonl.gz` in the same directory.

Measured endpoint defects were number `0`, energy `-1.30e-18 eV/H`, and
maximum absolute species `1.86e-20`; the least photon stock was
`8.45e-19`, and the final gas was admissible. Three H-edge and two He-energy
physical Jacobian columns were compared with finite differences; the maximum
relative discrepancy was `1.22e-8` in an H-edge column, with absolute
discrepancy at most `6.82e-21`. These checks validate this small numerical
lane and its accounting. They do not establish grid convergence, physical
production readiness, or equivalence to the upstream EoR calculation.

## Independent tolerance and shear references

Four additional exact-model integrations used the same physical RHS SHA256
`6df06662108635b525eea75b1ce2cdbcd91afe64a21ed0076977088c2fe5d63c`
and native binary SHA256
`22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5`.
Each case has an atomic JSON result and a valid gzip native-call record under
`/root/HE25_NCP_BIRTH_20261016/references_final/`. The four case names are
`q0_radau_tight`, `qm005_radau`, `qp005_radau`, and `q0_dop853_tight`.
The first used `rtol=3e-11, atol_scaled=3e-13`; the two shear cases used
`rtol=1e-10, atol_scaled=1e-12`; DOP853 reused the tighter q=0 tolerances.
Their elapsed times were respectively 37.44, 31.89, 31.26 and 8.33 seconds.
All completed without a retry and retained positive minimum photon stocks.

The original q=0 Radau pilot compared with tight Radau differed in final gas
temperature by `2.66e-14 K` and at most `3.90e-18` in any gas state coordinate.
Tight Radau and tight DOP853 differed by `1.78e-14 K`, `2.60e-18` in gas
coordinates, and `5.56e-22` in photon number. The largest absolute number,
energy and species ledger defects among the four results were respectively
`3.39e-21`, `3.04e-18 eV/H` and `3.86e-20`. These are measured tolerance
stability and cross-integrator checks at one momentum grid; they do not by
themselves establish grid convergence or the transport method's accuracy.
