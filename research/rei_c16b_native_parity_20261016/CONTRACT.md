# C16B native point parity — frozen mechanical execution contract

Authority: parent task/user scope and repository AGENTS.md. Scientific framing
was assigned to this agent with requested Astra role; runtime model identity is
not independently observed. This contract fixes implementation and acceptance;
the coding worker must return substantive scientific ambiguities to the reviewer.

## Immutable inputs and allowed changes

- Research base: PR155 `f8f26710e3961609acf4d7e7930bc7b2a95bd39c`, checkout
  `/root/REI_C16B_NATIVE_20261016/repo`.
- Native authority: current PR150 branch
  `origin/research/flrw-production-integration-20261015`, exact commit
  `0e25846433170d0f420c4cda44a0bedbf02cd177`. Execute the exported crate at
  `/root/REI_C16B_NATIVE_20261016/native/rust/rei_microphysics`.
- Allowed code: new native `examples/c16b_native_parity.rs`; identical archival
  example and Python comparator/tests/documentation under new research directory
  `research/rei_c16b_native_parity_20261016`; task-local logs/results. Existing
  native science files, run directories, synthetic bridge, and historical evidence
  remain unmodified. Do not change native Cargo dependencies or scientific APIs.
- Bind native source identity by comparing tracked crate files to the exact Git
  source or recording an equivalent minimal export check. The executed example
  must be identical to its research copy. Preserve raw output and invocation.

## Required native execution path

Use original public APIs `CovariantTransport::{new,empty_state,add_delta,prepare}`,
`PreparedAbsorption::evaluate`, `IgmGasState::from_temperature`, `igm_rates`, and
`igm_point_rhs` (or original `AxbiProvider` delegation to both). Use the original
`AtomicProvider::reference()` through native transport preparation; do not copy
Verner formulas into the Rust example. Native constants may be read from
`HHeModel::controlled_fixture`, but its synthetic reaction provider is forbidden.
Call the original native point RHS with photo on and `IgmPhotoInput::default()`
at exactly the same gas, density, temperature, h, and CMB temperature.

Original CI floors, RR, DR branch, CE caps, freefree, CMB and Case-A escape stay
active and untouched. In particular, never replace them with Python manufactured
coefficients and never call the synthetic thermal bridge in this comparator.
The native absorption operator owns the photon sink once; the point RHS consumes
its photo rates and owns chemistry and energy terms. It adds no second sink.

## Normalization and frozen physics

All photon counts `N_k` are per H nucleus, including native `PhotonState.number`.
Native `energy_ref` is q*N in eV/H. Python gas stocks are per H; native fractions
are `[HII/H, HeII/He, HeIII/He]`. For helium abundance Y=nHe/nH,
`a_i=[1-x, Y*(1-y-z), Y*y]` and proper absorber densities are `nH*a_i`.
Use proper nH in cm^-3 and proper dt in seconds. Set mean expansion h=0 for
these frozen geometry point tests, including nonzero b.

For reference geometry `(1,1,1)`, current scale factors are
`[a*exp(-b), a*exp(-b), a*exp(2*b)]`; use a=1. Photon energy is
`E_k=q_k*sqrt((1-mu0^2)*exp(2b)+mu0^2*exp(-4b))/a`.
Map the original reference ray mu to Python, not current mu. No additional
angular weight, volume factor, 4*pi, or geometry drift is applied to stored N.

Physical binding chi is `[13.598434599702,24.587389011,54.41776]` eV;
Verner activation thresholds are `[13.60,24.59,54.42]` eV. Equality at a fit
threshold is active and generally has positive E-chi heat. Sigma is zero below
the fit threshold. eV-to-erg is `1.602176634e-12`; c is `2.99792458e10` cm/s.

For each fixed-opacity node, define

```
kappa_k = sum_i nH*a_i*sigma_i(E_k)                # cm^-1
Nstar_k = N_k/(1 + dt*c*kappa_k)                 # backward Euler survivor
Gamma_i = c*nH*sum_k sigma_i(E_k)*Nstar_k         # s^-1 per absorber
Heat_i = c*nH*sum_k sigma_i(E_k)*Nstar_k*(E_k-chi_i)*eV_erg
A_i = dt*a_i*Gamma_i                            # events per H
```

At dt=0, Nstar=N and A=0, but Gamma and Heat remain instantaneous nonzero rates.
At finite dt, feed a Python state with Nstar into the existing source-locked
`src/native_photo_contract.py::photo_point`, importing the existing C16B
`source_aware.py` explicitly. Independently calculate Nstar from original
Python Verner opacities; do not set Python counts from Rust output. Compare
survivors as well as all three Gamma and all three Heat entries.

Use delta states with at most one distinct q per ray/cell. A mixed spectrum
must occupy distinct cells or rays so two-moment spectral reconstruction does
not replace a set of deltas by a continuous closure. Return native node count,
input nodes/rays, actual energies, gas/EOS state, all six photo inputs, survivor
arrays, absorption ledger, native rates, and complete photo-on/off RHS fields.

## Required bounded cases

1. Each fit threshold separately: below/equal/above at b=0, dt=0 and finite dt.
   Use adjacent representable values or a documented small relative separation;
   equality must reach the actual native atomic evaluator exactly. Record actual
   E and branch truth. Do not widen a threshold or silently move an equal case.
2. A simultaneous 20/40/80 eV reference spectrum with positive unequal per-H
   counts, each native absorber nonzero, b=0,+0.1,-0.1, dt=0 and finite dt.
   Include nonzero-mu rays and report actual energies for geometry parity.
3. Stiff finite absorption: choose dt so max(dt*c*kappa)>=1e6, finite denominator,
   and positive surviving photons. Include a nonstiff finite case with maximum
   exposure around 0.1–1. This tests the frozen-opacity operator only, not a
   coupled chemistry integrator. Never form/claim a giant explicit gas step.
4. Native point temperatures include 100 K, 1e4 K and 1e5 K at mixed nonzero
   ionic fractions, exercising low/high DR branches, native cold floors/caps,
   and finite collision/recombination/cooling. CMB cases include Tcmb<T and
   Tcmb>T. Temperatures are interior to the strict native domain [1,1e6] K;
   use EOS recovered temperature to compare exported rates.
5. Photo-off/empty-photon control and an absent-absorber control (e.g. no He)
   distinguish per-absorber rates from event rates and ensure no division by
   absent species. No-He fractions derivatives must be zero.

Cases may share fixtures and combine this matrix compactly. Freeze exact case
values in the comparator source/output before interpreting results. The parent
owns the separate 64-case synthetic benchmark; it does not satisfy native tests.

## Numerical acceptance and ledgers

Gamma and Heat: componentwise `abs(R-P)<=1e-12*max(abs(R),abs(P))` for nonzero
values. If analytically zero (empty spectrum or all support below threshold),
require exact floating zero: these are sums of explicitly zero terms, so no
universal dimensional absolute floor is justified. Report maximum relative error
only over nonzero comparisons and report zero comparisons separately.

Survivor/event/energy positive quantities use the same 1e-12 relative bound.
For identities and cancellation differences, accept
`abs(residual)<=128*eps*sum(abs(terms))`, eps=2^-52, using the actual participating
gross terms in matching units; zero gross scale requires exact zero. This is a
roundoff bound for short binary64 expressions, not a replacement relative bound
for Gamma/Heat. Report raw residual, gross scale and normalized residual. Photo
on-minus-off tolerances include both operands so cancellation is not mislabelled.

Check each following identity with no invented reaction owner:

- Native H conservation: dHI+dHII=0; He conservation: dHeI+dHeII+dHeIII=0.
- Charge: de=dHII+dHeII+2*dHeIII, using native chemical density derivatives.
- Photon sink: sum_k(N-Nstar)=sum_i A_i; per-channel native A_i=dt*photo_events_i/nH.
- Photon energy: sum_k E_k*(N-Nstar)=native absorbed binding+heat,
  and equals dt*photo_input_erg_cm3_s/(nH*eV_erg).
- Full native microphysical ledger:
  thermal_micro+binding_micro+escape-cmb_to_gas-photo_input=0.
  CMB reservoir has sign `-cmb_to_gas`. For h=0,
  nH*w_dt=thermal_micro; if h is ever nonzero its native expansion work must
  be included separately, not interpreted as microscopic loss.
- Reconstruct binding rate from native species derivatives:
  eV_erg*(chiH*dHII+chiHeI*(dHeII+dHeIII)+chiHeII*dHeIII)=binding_micro.
- On-minus-off species derivatives equal stoichiometry of photo event rates;
  delta thermal equals sum_i absorbers_i*Heat_i; delta binding equals
  sum_i chi_i*eV_erg*photo_events_i; delta photo_input equals their sum.
  Escape, CI/RR/DR/CE/freefree/CMB, and expansion terms are identical on/off
  at fixed state (exact equality where the same deterministic calls are used).
- Inspect/export RR/CI/DR/CE/freefree/CMB terms to establish use of active native
  owners. Do not demand every process nonzero in every case; low DR is exactly
  zero by native policy. Show representative nonzero channels in appropriate
  temperatures and CMB sign cases.

Check temperature derivative consistency with EOS particle-number variation as
an algebraic native point identity. No finite-time thermal trajectory is claimed.

## Execution, return and stopping rule

Use `CARGO_BUILD_JOBS=2`, `cargo build --release --manifest-path <native>/Cargo.toml
--example c16b_native_parity -j 2`, then bounded `timeout 300s` native/comparator
execution. Total concurrent compilation <=2 CPU cores, working memory <=8 GiB;
native example single transport worker. Thread-limited Python where libraries
need it. No remote campaign, source-model edit, full production run, history
integration, benchmark expansion, or publication.

Return changed-file diff, command/exit/resource record, exact source identity,
raw JSON/JSONL outputs, per-check summary, and a concise README command. A failed
scientific criterion, missing immutable source, ambiguity, or required model edit
returns HOLD with its concrete mismatch; do not relax a tolerance. One reviewer
pass may authorize a bounded targeted repair, followed only by affected tests.
All checks passing transitions directly to independent read-only review and the
scoped decision, then stops. Admission ceiling is native point photo parity and
energy ownership with fixed-opacity finite-dt absorption. Cosmological history,
coupled solver convergence, continuum accuracy, physical fit accuracy and existing
synthetic-bridge production validity remain unresolved by this experiment.
