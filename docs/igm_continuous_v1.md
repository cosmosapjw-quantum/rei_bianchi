# Continuous-emissivity homogeneous IGM research path

## Scope

`igm_continuous` is an additive numerical research implementation for the same manufactured FLRW H/He fixture, atomic provider, Case-A escape closure, clumping factor 1, and primary-only photoheating used by the existing IGM tools. It changes the representation of the stated continuous source. It does not reinterpret a finite instantaneous-birth history as the same numerical problem.

The existing `igm_history` implementation, configuration file, historical diagnostics, and accuracy-failure records remain separate. Conservation and positive accepted states do not establish temporal accuracy, spectral convergence, or physical validity as an observed reionization model. Numerical acceptance requires independently controlled time integration, spectral quadrature, output sampling, and reference accuracy. This path does not implement checkpoint/restart.

## Continuous source and characteristic coordinates

Write `s = ln(a)` and `eta = ln(E) + s`, with photon energy `E` in eV. A fixed `eta` follows cosmological redshift exactly through `E(s) = exp(eta - s)`.

The source is `j_total` photons per H nucleus per proper second. Its normalized photon-number spectrum is

```
p(E) = 1 / (C E^2),  Emin < E < Emax
C = 1/Emin - 1/Emax.
```

Since `dE = E d eta`, the source density per unit `eta` is `j_total E p(E)`, not `j_total p(E)`. A positive quadrature node `(eta_j, w_j)` therefore has proper-time source rate

```
S_j(s) = j_total w_j / (C E_j(s))
```

while its characteristic lies in the source band. Its continuous equation is

```
dN_j/ds = [S_j(s) - sum_i kappa_ij(s) N_j] / H(s),
kappa_ij = c n_i sigma_i(E_j).
```

There is one conversion from proper time to `ln(a)` time. Counts are already per H nucleus; no additional `a^3` factor or dilution term is inserted. The fixed domain covers the union of all emitted spectra: `[s_start + ln(Emin), s_end + ln(Emax)]`. Initially every characteristic has zero photons, including nodes that enter the source band later.

## Spectral quadrature

`--spectral-panels` is a new, explicit positive integer. It controls composite two-point Gauss quadrature in `eta`.

- `--spectral-grid uniform` is the default: that many panels cover the full characteristic domain.
- `--spectral-grid threshold-bands` partitions the domain at the initial and final mapped source edges and the HI, HeI, and HeII Verner cutoffs. Specifically, retain the domain endpoints and every strictly interior `s_start + ln(E)` or `s_end + ln(E)` for `E` in `{Emin, Emax, cutoff_HI, cutoff_HeI, cutoff_HeII}`, then sort and deduplicate. The panel count applies independently to each resulting segment.

Every panel supplies two positive nodes. The full node count is checked against the existing `max_packets` resource limit before node allocation. Nodes are fixed throughout a run, so storage does not grow with the number of accepted timesteps.

The legacy configuration fields `birth_panels` and `energy_panels` are not used to construct this path's source or spectrum. The existing strict configuration parser still validates those fields, but the new spectral controls determine the new quadrature. The original configuration bytes and the actual runtime overrides are recorded separately.

Weights are never renormalized. Emitted number and energy ledgers accumulate the actual finite quadrature source, not a substituted analytic total. Error in approximating the analytic continuous source moments must be measured separately. Changing the spectral grid is a distinct approximation change requiring its own refinement checks, including instantaneous endpoint photoionization rates.

## Event support and time stepping

For each characteristic, source entry and exit occur at `eta_j - ln(Emax)` and `eta_j - ln(Emin)`. Absorption support changes occur at `eta_j - ln(cutoff_i)`. The integrator stops at ordered event coordinates and requested output coordinates.

Source activity on an event-bounded interval `(s0, s1)` is determined from overlap with its open interior: `entry < s1` and `exit > s0`. Channel `i` is active on that interval only when its cutoff crossing is later than `s0`. Explicit channel masks are applied consistently to opacity, the photon denominator, photoionization, heating, and absorption ownership. Photon energies are not shifted to manufacture a desired branch.

Normally the spectral energy and background are evaluated at the midpoint `sm`, with `dt = (s1 - s0)/H(sm)`. The coupled source-aware backward Euler update is

```
N_new = (N_old + dt S_mid) / (1 + dt sum_i kappa_i(new gas)),
A_i = dt kappa_i(new gas) N_new.
```

The gas solve uses these same absorption owners. Global temporal accuracy remains first order because the chemistry/thermal transaction uses backward Euler; symmetric redshift bookkeeping does not make the full method second order.

Distinct floating-point event times can be adjacent representable numbers, leaving no representable midpoint. These positive-width intervals are not merged or skipped. Only in that case, the stage is evaluated at the right endpoint using the same explicit interior support masks. The actual interval width remains in `dt`. `endpoint_stage_steps` records accepted instances of this fallback in the state, CSV, and status output.

Physical endpoint Gamma is evaluated separately from the interval photo input used by the gas transaction. Exact-cutoff output uses the post-event, right-hand channel convention. HI-cutoff survivors are exported at the cutoff with both number and energy recorded; photons emitted below the tracked HI band are immediate source outflow.

## Conservation and positivity

For one fixed-energy transaction, the same `A_i` defines photon depletion, primary ionization counts, binding-energy deposition, and heat. The midpoint photon energy is used consistently in both absorption energy and source energy.

Redshift is recorded in two parts: old photons lose energy from the initial to the stage energy; surviving photons lose energy from the stage to the final energy. Newly emitted photons enter at the stage energy. Together with the source-aware BE number/energy identities, this makes the local redshift, absorption, source, and material ledgers telescope without an independently adjusted energy correction.

The existing strict gas-domain admission, species constraints, shared-owner checks, and number/energy tolerances are retained. There is no photon floor, state clipping, arbitrary packet deletion, or source-weight normalization. Invalid source arithmetic is rejected. Characteristic identities and log-counts are retained for extinguished floating-point readouts, with explicit IEEE-underflow bounds; a zero readout is not interpreted as physical extinction. Only physical band outflow removes a surviving inventory from the active radiation budget.

Accepted transactions update the state together. Failed trials operate on private candidates and cannot partially update the caller's accepted state.

## Rust APIs

The additive history API is in `rei_microphysics::igm_continuous`:

- `ContinuousHistory::new(config, spectral_panels)` selects the uniform grid.
- `ContinuousHistory::new_with_grid(config, spectral_panels, SpectralGrid::ThresholdBands)` selects the mapped threshold partition.
- `advance_one` and `advance_to` return a new accepted state.
- `radiation`, `balances`, and `endpoint_photo` expose the radiation inventory, conservation residuals, and physical endpoint photo rates.

The original `implicit_step` remains available. The additive `implicit_step_with_source` and `implicit_step_with_source_masked` accept proper source rates at the supplied packet energies. Masked opacity and photo evaluators are also available. Unmasked and all-active-mask paths retain the original provider cutoff semantics.

## Reproduction and outputs

From the repository root, with Rust available:

```sh
cargo test --manifest-path rust/rei_microphysics/Cargo.toml
cargo build --release --manifest-path rust/rei_microphysics/Cargo.toml \
  --example igm_continuous

rust/rei_microphysics/target/release/examples/igm_continuous \
  --config configs/igm_manufactured_v1.cfg \
  --output NEW_CONTINUOUS_DIRECTORY \
  --spectral-panels 32 \
  --spectral-grid threshold-bands \
  --max-dln-a 7.8125e-7 \
  --output-panels 20
```

If `CARGO_TARGET_DIR` is set, use the executable under that target directory instead. The displayed grid and step size are reproduction controls, not a declaration of numerical acceptance.

The output directory must be new; existing directories are rejected. Outputs include:

- `config.cfg`: original input bytes
- `manifest.json`: source mode, grid, node count, actual step/output overrides, source/config identities, clock convention, and research limitations
- `nodes.csv`: fixed `eta` nodes and weights
- `history.csv`: the established IGM comparison fields, plus step/resource diagnostics
- `nodes_final.csv`: final energies, source activity, count readouts, and retained log-counts
- `status.json`: completion flag, attained time, accepted/rejected steps, endpoint-stage count, and error if applicable

A runtime integration failure returns a nonzero exit status and writes `complete=false` at the last accepted state. CSV rows contain completed scheduled outputs; the status can therefore be later than the final CSV row. A partial output is not a completed history and cannot be resumed through this CLI.

The independent continuous reference uses a separately implemented coupled RHS and integration algorithm. Its own grid/time controls, source identities, number/energy budgets, and retightening checks must be examined before comparison. The existing `tools/igm_compare.py` retains the original field and conservation criteria; no historical failure is replaced merely because this new path compiles or closes its ledgers.
