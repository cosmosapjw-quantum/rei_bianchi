# REI-ACCEL02: C02B resume, native broad evolution

Campaign path retains the pre-existing `20261011` identifier. Execution receipts use the actual UTC timestamps (2026-10-10); these are not a claim of future execution.

- RUN002 is reused. No RUN002 solver or scientific-verification replay.
- N1: actual low-temperature Case-A H/He/thermal provider binding, independently accepted within declared source/IC/CMB limits.
- N2: actual z15.9→4 (~1.2713 Gyr) coupled H/He + temperature + photon histories computed. Event handling fixes late50keV source-entry stalls and analytically excludes dormant modes.
- EVENT_COUPLED002: combined endpoint+saved-epoch energy residual5.248e-11 and photon-number residual5.010e-10 pass their frozen1e-9 bounds. All nine same-grid time comparisons pass2e-6 (max1.423e-8). The original run did not explicitly measure all accepted gas states; saved epochs pass. This is a scoped temporal result, not a continuum certificate.
- N4: existing BASS PR137 receipts adopted, independently reviewed, published as BASS PR140. No replay. These are the two original reduced histories, not this new native history.
- Remaining gate: energy/angular discretization and Bianchi paired history. EVENT003 is the next new full-interval spectral diagnostic, not a rerun of old RUN002.

## Scope

Conditional initial T20K,xHII2e-4,neutralHe at z15.9; source-bound HM12 author UVB initial field and evolving emissivity10–50000eV; imported Grackle Case-A RR/CI/DR/CE/ff; prescribed isotropic CMB heat bath. CR, RCT, secondary cascades, diffuse recombination transport, radiation stress backreaction are not included. Mean-scale-factor redshift is not directional observed redshift. Native ionic fractions are not the earlier Case-B filling factorQ.

## Entry points

- `n1/CONTRACT.json`, `provider.py`, `ABI.json`, native Rust crate.
- `n2/run_event_coupled.py`: event-aware integration of exact `integration/run_native_history.py`.
- `n2/evidence/EVENT_TIME_COMPARISON.json`: exact producer identities and frozen time/ledger checks.
- `integration/evidence/NATIVE001/`: first actual failure retained, including exact as-run source.
- `review/`: independent decisions; read the latest bounded decision before making a promotion claim.
- `publication/`: Git and dual-backup receipts.

Build the crate in `n1/native` with Rust1.90.0. Python requires NumPy/SciPy. New run directories must be create-only. A restart snapshot is evidence unless a supported restart entry point explicitly validates its source and active event state; do not claim automatic continuation from a bare NPZ.

Preserve all failed first attempts. Do not lower tolerances, clip invalid gas/photon states, replace source/closure, or repeat completed reduced-model validation to manufacture progress.
