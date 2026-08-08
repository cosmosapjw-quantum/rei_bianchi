# Results and verdict — R2B-R2A-R2-R1

## Verdict

```text
DURABLE_PASS_R2C_R1B_R2B_R2A_R2_R1_
HUMMER_SEATON_NODAL_V_TABLE_LOCK_
F_INTERVAL_ONLY_AND_FOUR_CORNER_BRANCH_ENVELOPE_
EXACT_HEII_LYA_ENERGY_LOCK_
TWO_PHOTON_AND_FREE_BOUND_FIRST_MOMENTS_UNRESOLVED_
BOUNDED_KERNEL_PROPAGATION_PREFLIGHT_AUTHORIZED
```

The source branch/energy theory audit is complete.  It is not a production-history pass.

## Main results

- Hummer--Seaton nodal `v` table recovered: `0.285,0.305,0.325,0.350,0.375` at `log10 T=4.00,4.25,4.50,4.75,5.00`.
- Historical interpolation algorithm not identified.
- `f` identified only as absorbed fraction in `[0.1,1]`.
- 21,600/46,080 nodes (46.875%) are below the `v` table.
- Four-corner multi-affine branch envelope closes every node.
- Negative branch multiplicity count: `0`.
- Maximum photon-count identity residual: `4.4408920985e-16`.
- Exact He II Ly-alpha energy: `40.813320 eV`.
- Exact Ly-alpha excess: `27.214885400298 eV` on H I and `16.225930989 eV` on He I.
- Two spectra with the same `ell,m`, two-photon count and total pair energy give different first moments; first-moment uniqueness is disproved constructively.
- All unidentified OTS energy has one owner in the unresolved OTS ledger.

## Authorization

```text
R2C_R1B_R2B_R2A_R2_R1_completed = true
R2C_R1B_R2B_R2A_R2_R1A_authorized = true
production_history_authorized = false
production_node_chemistry_authorized = false
R2C_R2_authorized = false
B2C2B_authorized = false
```

## Next bounded stage

```text
P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1A-
FOUR-CORNER-BRANCH-AND-UNRESOLVED-OTS-ENERGY-PROPAGATION-PREFLIGHT
```
