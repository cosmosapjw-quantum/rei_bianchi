# SOURCE_AGE_NATIVE_OWNER_BIND: frozen local contract

Source base: PR164 `a50d176b56d267b651d204f371204f61299b9a64`; prior
chemistry result PR160 `8351f21036eeaa079e603159a08269dbe90ce58e`.
The native source chosen for this bounded run is PR150
`35d9747a0bbedcafdb568467ce7c1e7a25f965b6`. Its Grackle rates,
thermal, covariant transport and MD14 source files have the same Git blob IDs as
the historical PR160 native source `a42fd7c9849306074a9f7a262628cd852ce34dea`.
Its driver has an additional BASS background dispatch, so source-age code must
use `Driver::geometry_point` and `geometry_increment` for a selected provider.

## Physical mapping

Use the native `(-,+,+,+)` convention and proper time. Let
`x=ln(a/a_ref)`, birth coordinate `y`, and `dt=dx/H`. Native MD14
`AxbiSource::at_redshift` returns `per_h_s`, photons per comoving H per proper
second. Thus `j(y)=dN/dy=per_h_s/H(y)` and a positive quadrature node of width
`w_y` creates `per_h_s(y)*w_y/H(y)` photons per H. The native SFR/yield already
has its year units cancelled. This source has a conditional 50,000 K blackbody
over 13.6–100 eV; it supplies photon birth time, not an SSP lifetime model.

For a native reference ray with current `RayGeometry.scale=r(a)`, the stored
reference photon energy is `q=E_birth/r(a_birth)`. `DriverConfig.q_ref` is a
background shear parameter and is unrelated to this photon q. In LRS Bianchi
geometry with `s=db/dt`, `a_perp=a exp(-b)`, `a_parallel=a exp(2b)`, a birth ray
obeys

`E(x)=E_birth exp(y-x) sqrt(exp(2Δb)(1-μ_birth²)+exp(-4Δb)μ_birth²)`,

`-dE/dt=E[H+s(3μ²-1)]`.

Signed `s/H` and physical nonnegative `Sigma=sqrt(3)*abs(s)/H` are distinct.
The Verner fit activation energies `(13.60,24.59,54.42)` eV are distinct from
the native binding energies `(13.598434599702,24.587389011,54.41776)` eV.

## Single-owner coupling

Each positive birth cohort retains its own complete native `PhotonState`,
birth interval/clock, physical energy support and birth direction. The native
two-moment cell reconstruction is nonlinear, so a merged population's
survival ratio cannot be apportioned afterward to infer surviving ages.
Prepare each cohort with unchanged native `PreparedAbsorption` and evaluate all
against the *same* trial absorber stocks. Sum the resulting native photo Gamma,
heat and event terms into one `IgmPointRhs` and one gas Newton solve. The
returned per-cohort survivor states are the only photon sink. The legacy
`chemical_stage` path remains the one-cohort comparison control.

Process positive MD14 birth nodes in chronological proper time. Split the
chemical interval at birth nodes so no photon can absorb or do geometric work
before birth. An accepted bundle owns gas, every cohort, aggregate diagnostic,
source cursor, clock and ledgers; rejection discards the entire trial. Use
native geometry work and gas adiabatic update once. Case-A escape remains
bolometric energy; no photon number, spectrum or pressure is inferred for it.

For `Y=nHe/nH`, binding per H is
`B=χH*xHII+Y*(χHeI*xHeII+(χHeI+χHeII)*xHeIII)`.
Check photon number, species/charge and thermal+binding+radiation+escape+CMB+
geometric-work ledgers per accepted step and cumulatively, with native
physical-gross normalization `1e-10`. Preserve raw residual and scale.
Positivity and native temperature domain `[1,1e6] K` are hard trial checks;
there is no clipping. The native 50-iteration Newton, `1e-11` residual and
40 line-search halvings are fixed for parity. Expect first-order proper-time
convergence of backward Euler; PR164's second-order frozen-stock per-ray result
does not transfer.

## Admission boundary

The actual execution must establish which source, provider, interval and
resolutions ran. A finite short-epoch PASS does not establish an EoR history,
continuum convergence, stellar SSP age physics, an escape spectrum, or
Einstein backreaction. `PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.
