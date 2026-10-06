# Manufactured homogeneous FLRW H/He history: numerical checkpoint

## Status: endpoint and software gates pass; accuracy gate FAILS

This is a manufactured numerical wiring experiment, **not an observed EoR reconstruction, bubble-volume fraction, interval certificate, or validated physical prediction**. The fixed synthetic model reaches z=11.5 from z=12 with initially empty photons, xHII=2e-4, exactly neutral helium, and T=30 K. Conservation, immutable rejection, source ownership, cutoff handling and restart tests pass. The finite source-quadrature and first-order split backward-Euler implementation **does not meet the frozen independent-match and refinement targets**. Do not promote this checkpoint to a scientific baseline.

The CLI `status=complete` means the requested integration endpoint was reached. It does not mean the independent numerical validation passed. The accompanying `validation_status.json` records that separate failed gate.

## Model and units

All cosmological/source numbers are explicitly synthetic and frozen in `configs/igm_manufactured_v1.cfg`: H0=2.2e-18 s^-1, Omega_r=9e-5, Omega_m=0.3, Omega_b=0.048, Omega_Lambda=0.69991, YHe=0.24, Tcmb0=2.7255 K. Constant escaping emissivity is 1e-15 photons/H/s with photon-number SED proportional to E^-2 on [13.7,100] eV. No second escape factor or external Gamma is added.

The low-temperature Grackle 3.4.1 subset, Verner cross sections, Case-A escape, clumping C=1 and primary-only electron heating are unchanged. Atomic binding energies and Verner cutoffs remain distinct. All three absorbers compete above the HeII cutoff. Thermal energy is erg/H; packets are photons/H; the only history coordinate is ln(a). No Bianchi, diffuse recombination photon, secondary-electron, molecular/metal, or bubble model is included.

## Algorithm and boundaries

Positive composite Gauss2 source quadrature uses fixed ln(a) panels and positive energy nodes split at binding and actual cross-section thresholds. Finite weights retain the analytic SED normalization: quadrature error is measured, not removed by a discrete renormalization. Gas timesteps cannot change the birth schedule.

Each accepted step applies exact characteristic redshift to the endpoint, followed by a common-endpoint backward-Euler gas/photon solve with analytically eliminated photons. Proper-time rates are multiplied by delta_ln(a)/H_endpoint once. This is a quadrature weight, not an exact elapsed-time clock. The existing RHS owns expansion work; the history does not apply a second adiabatic map. Species production/destruction updates preserve the closed simplex. The scalar energy root uses safeguarded Newton inside a legal actual-EOS bracket, falling back to bracket subdivision. Every accepted candidate must satisfy the original coupled BE residual and conservation tests. No lagged root, after-step clipping, positive floor, or temperature projection is accepted.

The actual recovered EOS must lie in 1..1e6 K. Exact static roots at admitted endpoints are preserved. Near machine precision, neighboring energy values are searched until a local residual minimum is found. Domain-invalid candidates reject without mutating the accepted state.

A step stops at births, requested outputs and packet cutoff crossings. At an exact crossing, the incoming interval evaluates that channel at its exact cutoff (active); the next interval is below it. Survivors crossing HI are counted as outflow with their crossing energy. Photons born below HI are immediate outflow. Source photons are inserted after evolution to their birth coordinate, once only. No packet merging is performed.

## Underflow representation

Strong extinction is inevitable in this fixture. A positive packet keeps its identity and finite log weight even after an IEEE count readout becomes subnormal or zero. Normal counts use the conservative BE arithmetic directly and store ln(count); in the tail, the log weight evolves independently as logN_new=logN_old-log1p(dt*kappa). Thus this is a **hybrid count/log representation**, not a claim that normal-range log arithmetic is the sole authority. Initially zero photons are an empty packet list, distinct from an extinguished born packet. Packets are removed only at physical HI outflow.

Float-facing underflow at the photo adapter is explicitly bounded in its physical units. Dropped per-absorber Gamma is converted to event/H/s by absorber/H; dropped heat is converted to erg/H/s the same way. Accepted-step bounds integrate with the same dt. An underflowed count contributes a conservative MIN_NORMAL remaining-count stock bound, with its packet energy bound. A previous stock bound covers later zero readouts of the same extinct packet. Bounds are never accumulated on rejected trials. Hard limits are 1e-20 photons/H and 1e-30 erg/H, far below physical comparison allowances. The gas, opacity and thermal-provider normal-intermediate contracts are unchanged. No source parameter was changed to avoid extinction.

## Ledgers and frozen acceptance criteria

The ledger contains emitted number/energy, absorption by species, active photons, HI outflow, redshift loss, gas thermal and binding energy, escaped atomic radiation, expansion work, signed CMB reservoir and the integral of absolute CMB exchange. It also records CI/RR/DR events, provider floor/cap/excluded contributions and underflow bounds. Each accepted composed step checks local identities directly and checks the cumulative residual anew. Subtracting two large cumulative residuals is not used to estimate a tiny local loss.

Ledger tolerance is 1e-10 times **cumulative positive throughput**, with floors 1e-10 photons/H and 1e-20 erg/H. The history passes those cumulative scales explicitly to the stepper; standalone step tests retain the floors. This corrects an initially over-strict local-throughput implementation; it does not change the approved tolerance. Cumulative admission prevents Nstep-times-tolerance drift. The nonlinear endpoint residual is 1e-15 times its coordinate scales (stricter than the original 1e-13 proposal).

Independent-match targets remain: fractions and ne/nH 1e-6 absolute +1e-3 relative; T 1e-6 K +1e-3 relative; Gamma 1e-22 s^-1 +1e-3 relative; number/event ledgers 1e-8 photons/H +1e-3 relative; energy ledgers 1e-20 erg/H +1e-3 relative. Tests did not relax these values to obtain a pass.

## Measured timestep refinement

These runs hold all 640 source births and energy nodes fixed. The independent continuous ODE reference uses Radau and retained optical depths, not the Rust BE algorithm. Ratios below are maximum error divided by the unchanged allowance; passing requires <=1.

| max delta_ln(a) | accepted steps | T ratio | HeII ratio | Gamma_HI ratio | redshift-energy ratio |
|---:|---:|---:|---:|---:|---:|
| 2e-4 | 232 | 67.26 | 88.91 | 40096.8 | 9274.4 |
| 5e-5 | 820 | 67.02 | 85.86 | 17538.1 | 2418.0 |
| 1.25e-5 | 3164 | 27.67 | 36.80 | 2711.6 | 633.3 |
| 3.125e-6 | 12560 | 7.51 | 10.28 | 361.69 | 159.51 |

The finest run took about 39.7 seconds in the measured environment. The largest Gamma_HI error is not merely an irrelevant vanished packet: at z=11.97453 the reference total is 1.67596e-15 s^-1 and Rust gives 2.28218e-15 s^-1, an absolute difference 6.06217e-16 s^-1. At that output T differs by 30.51 K and HeII by 0.001093. The late refinement trend suggests several million uniform steps for the most restrictive Gamma target; this is an extrapolation, not an executed or certified convergence result, and exceeds the declared 200000-step resource bound.

## Independent source/energy refinement and next numerical unit

See `igm_reference_v1.md` and the accompanying refinement JSON/CSV for independently integrated birth16/32/64 and energy2/4/8 probes. These do not confuse fixed-schedule ODE matching with convergence to a continuous source. In particular, replacing a continuous stiff source with sparse impulses changes instantaneous Gamma and the cumulative emission at intermediate output times even when the endpoint source integral agrees. The declared 20000-packet limit prevents treating a brute-force arbitrarily fine birth schedule as a demonstrated solution.

The next numerical remedy should retain this physical manifest and target the source/absorption discretization: for example an explicitly conservative exponential photon update with coupled integrated ownership, plus continuous-emissivity or photon-age quadrature that resolves newly born photons without millions of persistent impulse packets. Such a method needs its own plan, TDD, source/energy ownership proofs, independent comparison and separate refinements. It must not silently replace the source, lower accuracy targets or claim that homogeneous fractions are observed bubble fractions.

## Reproduction

From `rust/rei_microphysics`:

    cargo test
    cargo test --example igm_history
    cargo run --release --example igm_history -- --config ../../configs/igm_manufactured_v1.cfg --output NEW_DIRECTORY

The output directory must not already exist. Files include the exact config, hashes, manifest, birth schedule, history CSV, checkpoint and machine-readable status. A runtime failure exits nonzero and saves the last accepted checkpoint with `complete=false`. Use `--resume CHECKPOINT` with identical exact config bytes; use `--stop-after N` for a deliberate split run. Checkpoints retain all cursors, controller data, signed/absolute ledgers, log weights and provider/closure/schema/solver/source/config identities. Wrong identities or malformed state reject before mutation.

`sha256sum` is required for identity. Python is verification-only, not a Rust runtime dependency. See the reference document for portable SciPy/NumPy comparison commands. Generated plots are labeled manufactured and explicitly distinguish solver-completion from failed convergence. No external dependency was installed for this checkpoint.
