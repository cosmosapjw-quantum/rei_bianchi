# Original REI IGM: four-history radiation-stress consumer

This supplement consumes the same four complete original high-redshift histories
as [PR374](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/374), pinned at
`4554fc34765422f1c67e91c99ecac1bc9559fcce`.
It reads 1,248,952 saved states and provides 4,004 sampled physical diagnostic rows,
with extrema computed on all native rows. No coupled trajectory is newly evolved.

## Scientific decision

All four available histories satisfy the original omitted-stress and extra-energy
ceilings of 1e-4. The largest shear forcing is 1.02104978e-5 in delta_s/H,
approximately 0.8714 percent relative to the prescribed shear. Effective Omega_r
background radiation dominates; the actual ionizing-photon contribution reaches
only 1.25906452e-13 in delta_s/H. At q=-0.01 and mean redshift 4, the separate
shear and energy elapsed-clock diagnostics are +25.26856 and -56.68020 years.

The owner accepts these as four-case forced-background approximation diagnostics
for original AX03/AX08. The original family is still 4/5 and AX11/AX12 are open.
Central DAG remains **28/88**. This is not a coupled abundance error bound.

## Read and reproduce

- `REPORT_KO.md`: scientific results and scope in Korean.
- `DERIVATION.md`: metric, photon angular measures, SI units, shear and clock integrals.
- `SCIENTIFIC_OWNER_DECISION.json` and `DAG_OVERLAY.json`: exact scoped admission.
- `INPUT_MANIFEST.json`: original whole-file source SHA-256 values and row counts.
- `results/`: 4,004 derived rows, all-native extrema, parity and audit results.
- `figures/`: inspected PNG and editable SVG plus plotting provenance.
- `REPRODUCIBILITY.md`: authorized source recovery and executable commands.
- `STAGES.json`: all ten local R/C checkpoints; local SHAs do not imply public publication.

One consumer and one same-author adversarial audit were executed successfully.
No independent-author blind referee is claimed. The audit uses a separate scalar
CSV reader, cgs units and initial-momentum angular integration. Original source
accuracy and time/energy/angle refinements remain unresolved.

This public candidate contains the derived sample table, code, source hash pins,
scientific decisions and figures. Original four raw history files and private
workspace/conversation/backup metadata are retained separately. The source-full
recovery receipt is available through the pinned PR374 reference.

Next original-goal work is the actual +0.01 durable-checkpoint recovery in a new
bounded segment with original cumulative budgets, followed by the specified AX11
and AX12 runs. Further optional diagnostic catalogues are outside this unit.
