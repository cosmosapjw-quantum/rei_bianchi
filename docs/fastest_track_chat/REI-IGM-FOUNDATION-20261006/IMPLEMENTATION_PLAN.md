# First bounded unit: manufactured FLRW/HHe foundation

Approved design: FLRW_HHe_IGM_DESIGN_KO.md. Base HEAD 2b6005fd9c88e5cb38213c5bb66baee7caf54583; initially clean. No AGENTS.md found in workspace or repository. No S0 changes, commits, branches, pushes, chemistry/cooling admission, or full history integration.

## Interfaces and invariants

- `FlatFlrwConfig`: explicit H0 in s^-1, nonnegative Omega_r/m/Lambda, 0 < Omega_b <= Omega_m, 0 <= helium mass fraction < 1, Tcmb0 > 0, finite ordered ln(a) domain, nonempty parameter-source label. Flat sum tolerance 1e-12, no renormalization. No physical parameter defaults.
- `FlatFlrwBackground::new(config)` validates parameters and endpoint evaluations. `at_ln_a(ln_a)` / `at_redshift(z)` return `FlrwPoint`: a,z,H,nH,nHe,Tcmb,dt/dln(a),dt/dz and isotropic `GeometrySnapshot`. Domain restricted to finite representable positive density, temperature, volume and time factors. No `GeometryBackground::snapshot(t)` implementation until a real proper-time inversion is supplied; ln(a) is never passed as time.
- Density convention: rho_crit0=3 H0²/(8 pi G); nH0=(1-Y) Omega_b rho_crit0/mp, nHe0=Y Omega_b rho_crit0/(4mp). Explicit nucleon-mass approximation (mHe=4mp), neglecting binding/electron mass corrections. G=6.67430e-8 cgs, mp=1.67262192595e-24 g from NIST CODATA. Existing MPC_CM and HHeModel EOS constants reused.
- `IgmGasState {fractions:[f64;3], w_erg_per_h:f64}`: validated constructors/from_temperature; `eos(nH,nHe)` returns electron density,T,u; exact fractions permit all neutral/ionized simplex boundaries and zero He density. Strict positive thermal energy/T; no chemistry temperature admission claimed. Existing HHeModel electron/EOS validation reused, with no reaction evaluation.
- `adiabatic_to(a0,a1)` at fixed fractions: w1=w0(a0/a1)^2; caller supplies endpoint density. No new time integrator.
- Explicit adapters `w_erg_per_h_to_ev`, inverse; `primary_to_photon_packet`, `photon_packet_to_primary`, `primary_to_photon_node`, `photon_node_to_primary` use absolute comoving nH0 normalization. Existing CharacteristicRay/PhotonPacket transport bridge, no occupation-as-count conflation. All adapter inputs/outputs validated; reject overflow/positive underflow, preserve true zero.

## Execution/check sequence

1. Add focused tests with compilable minimal unimplemented stubs. Capture actual assertion failures (not missing-import errors) for background and state/adapters.
2. Implement minimum coherent modules/exports; get focused tests green. Tests cover independent H/density normalization, radiation/matter/Lambda limits, coordinate derivatives, endpoint geometry, exact adiabatic gas/photon scaling, zero electron/He/photon corners, composition/domain/flatness, NaN/inf/extreme overflow and adapter round trips.
3. Add frozen manufactured tracer example producing CSV from common ln(a) points through background, HHe EOS, RadiationState transport. This is analytical adiabatic wiring, not full non-equilibrium history or observed cosmology.
4. Run locked/offline full cargo tests, scoped rustfmt checks, clippy (classify pre-existing diagnostics), inspect exact diff. Record all logs, CSV, manifest/hashes and unfinished work. Independent review can read these after green.

Tolerances: normal analytic comparisons 1e-12 relative (no absolute floor that hides tiny densities); zeros exact; validation assertions categorical. No high-cost existing scientific campaigns rerun.
