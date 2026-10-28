# REI-GRID044-ENDPOINT-BINDING-01 implementation return

Executor: inherited `normalization_review` agent reused for bounded mechanical
implementation under the root's recorded routing exception. The attempted
lower-tier spawn was rejected by available agent capacity. This executor makes
no final scientific admission; source and baseline reviewers independently
review the delivered code, saved results and figure.

## Implemented path

`consumer.py` reads the exact saved `atomic_abundance_per_Href[:, -1]` column,
maps labels from donor Li7-before-Li6 to REC Li6-before-Li7 order, retains actual
neutron/tritium zeros, and calls the unchanged REC `target_response` with the
saved 2×6×3 rates and source multipliers `(1,1)`. It calls the unchanged WU
catalog, conservation, stoichiometry, ownership registry and source functions
to reconstruct the21 material source entries and fast-electron source.

Thirteen physical event identities each have one extent owner and two additive
source contributions. The additional physical key ignores arbitrary domain
and state-resolution prose, using the actual isotope/charge/ground-state/pool
signatures and the selected process/frame. The original WU synthetic energy
and photon helpers are unused. The original CR generic event ledger is called
with the actual saved `P/Gamma`, `chi`, and `K/Gamma` moments. The C23B spectral
assembler is unused and rejected as a substitute for these source moments.

The only new source algebra is

`F=(S-x*R)/r`,
`dF=(dS-R*dx-x*dR)/r-F*dr/r`,

with caller-coordinate derivative semantics, positive finite reference checks,
and explicit physical-to-per-reference mapping. The existing REC output and
Jacobian are already normalized and are not divided twice.

`rust/client.rs` uses the unchanged D5 gateway and computes `A*x` with `A`
assembled from WU incidence and saved physical photoionization coefficients.
It full-writes the21×21 `A` Jacobian. The point-time box is `[0,0]` at donor
proper elapsed time `9.742841244666013e16 s`. Per-isotope total bounds preserve
zero-width neutron/tritium coordinates. The positive-supported test point
keeps these coordinates at zero. No native norm is implemented or rerun.

## Observed endpoint outputs

Reference density `r=5.151254745827818 m^-3`; actual donor mean scale factor
`a=0.33333333333333326`; fixed comoving reference density
`n_ref0=0.19078721280843758 m^-3` at `a_today=1`.

Fast primary-electron number source:

- `6.113207047135675e-19 ref^-1 s^-1`
- `3.14906868137857e-18 m^-3 s^-1`

Signed collision energy transfers, ordered radiation loss / binding gain /
primary kinetic gain:

- `[-1.0118663544892516e-17, 8.339000234798153e-18, 1.7796633100943634e-18] eV ref^-1 s^-1`
- `[-8.35115562362068e-36, 6.882360343067273e-36, 1.4687952805534072e-36] J m^-3 s^-1`

These are an instantaneous source operator at the actual saved target under
the separately prescribed continuum pair. Thermal heating is `null` with
status `UNQUALIFIED`. HE's receiver record contains number and first kinetic
energy moments; it does not invent a monoenergetic spectrum, angular law,
finite-mass recoil law or stopping model. BASS's signed donor stress is a stock
in J/m³; new absorption transfer/stress rates and geometry feedback remain open.

## Executed tests and raw evidence

One initial changed-contract suite was executed in sequential stages. All32
Python checks and all9 Rust/REC comparison checks passed their recorded scoped
criteria. No scientific repair or repeated scientific suite was needed.

| Check | Observed row-scaled discrepancy |
|---|---:|
| WU species + fast-electron source versus REC | 1.924856455018995e-16 |
| Actual REC25×23 Jacobian versus complex-step | 1.488667807882561e-16 |
|26 component collision-energy partition | 1.582703458723587e-16 |
| Summed collision-energy residual | 0.0 |
| CR generic event-energy partition | 1.2345432226299177e-16 |
| Number source per-ref ↔ SI mapping | 1.3008491385081022e-16 |
| Energy per-ref ↔ SI mapping | 0.0 |
| Nonzero reference-source/density directional control | 2.147543150575634e-16 |
| Fixed-comoving scale-factor directional control | 8.367371580054058e-17 |
| Rust actual21 RHS versus REC | 0.0 |
| Rust actual21 Jacobian versus REC | 0.0 |

WU isotope, baryon and total material-plus-fast-electron charge residuals are
exactly zero in the decimal-representation rational arithmetic used by the
existing incidence compiler. This does not make the physical rates exact.

The two normalization mutations are distinct: omitting `-xR/r` changes the
manufactured source by `0.03812178499999999` in its stated units; omitting
`-F dr/r` changes the directional derivative by a row-scaled
`0.2024793964639783`. A deliberately wrong finite Rust Jacobian was admitted
by the unchanged callback gate but differed from the independent REC Jacobian
by a row-scaled `0.5`, as intended. Negative state, upper-bound violation,
outside-point time and an attempted time-derivative stencil were rejected.

The source CSV and PNG/SVG are in `figures/`. The executor viewed the saved PNG:
the exact-zero tritium contribution is labeled, all nonzero event contributions
fit the logarithmic axis, signed energy transfers occupy a separate panel,
and manufactured algebra controls are distinguished from physical source data.
An independent reviewer must supply the final figure review.

## Resources and preserved failure

`RESOURCE_RECEIPT.json` records all commands, actual exits and costs, including
the initial compiler failure:

- Scientific suite: `2.900492 CPU s`, `2.940682361000654 wall s`, peak measured
  science resident memory `105888 KiB`.
- Infrastructure: `14.682127000000001 CPU s`, `14.797034617000463 wall s`, peak
  measured resident memory `182628 KiB`.

The first Rust hello probe failed at linking because lld could not create a
requested worker (`Resource temporarily unavailable`). The original probe
script, stdout/stderr and failure receipt are preserved. A single targeted
infrastructure repair set one codegen unit and `-Wl,--threads=1`, reused the
already extracted compiler and standard library, and produced an actual
`RUST_PASS`. The actual client then compiled and ran. No systemwide install or
global environment mutation occurred. Compiler warnings about unused pieces
of the reused generic gateway are retained and did not prevent compilation.

Source inspection, remote calls and wrapper overhead are not measured and
are not represented as zero. Existing83, GRID044, HE reservations, new83 and
NCP allocations were neither reset nor transferred. Counts for new IVPs,
opacity integrals, old test replays, new83 and NCP are all zero.

## Remaining authority and obligations

Root owns final scenario/theory/report/DAG, admission, expected-SHA publication,
ZIP and provider backups. This returned unit leaves full physical domain,
trajectory accuracy/error control, secondary degradation/heating, angular
absorption transfer, new geometry feedback, full-network completion and L4
under their existing distinct gates. The runtime witness used in the Rust
test is a transparent caller assertion, not a native FP certificate.

No further provider execution is needed to inspect these saved outputs. Any
requested repair must state its specific finding and remain within the
cumulative new-unit limits and frozen stopping rule.
