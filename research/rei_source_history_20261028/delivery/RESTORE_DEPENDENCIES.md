# Restore immutable ANGTHERM dependencies

Use the existing `REI_ANGTHERM01_FINAL_20261023_46519489c540.zip`,15397188bytes, SHA256 `46519489c5406499a6c74c826fc53f1b02a46de6846773773ddc7476c0e7a036`. Its previously preserved dual-provider identities are referenced in `research/rei_fast_selected_20261028/intake/local_sources.md` and `CORE_SURVEY_SYNTHESIS.md`. The complete archive is not included or uploaded again by this unit.

`outputs/RESTORED_DEPENDENCIES.json` records the exact archive member, destination path, bytes and SHA256 for each of eight provider files restored by the coder. `delivery/DEPENDENCY_INVENTORY.json` records the remaining source/data dependencies. Restore the listed archive members below the existing `research/rei_fast_selected_20261028/inputs/angtherm_selected/` directory, retaining each member's `research/rei_angular_thermochemistry_20261023/` prefix. Compare bytes against the listed hashes before using the source.

The needed provider tree consists of `vendor/c22/atomic_network.py`, `vendor/c22/rr_energy_moment.py` and `vendor/c22/vendor/atomic/{r9_li_thermal_rates.py,phfit2.f,photo_table.dat,partial_table.dat,rrfit.f,rr_table.dat,rr_description.txt}`. The restored eight files total404006bytes. These are code and atomic tables, not retrieved paper bodies.

The same archive supplies `code/angular_model.py`, `inputs/background/grid044_history.npz` and `results/grid044_M4_nominal.npz`. Preserve nominal NPZ SHA256 `ac035e9bdc6427dd66cbc3a39db92769ffc23f2ae8de7a2c1200b83fb9f20619`. Reuse the PR245/PR243 model/config and population CSV at their inventory hashes. No donor integration is needed to restore or inspect these artifacts. This instruction does not authorize the new coupled IVP.
