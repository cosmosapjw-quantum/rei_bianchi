# Run state

- Implementation base: `03127d4ed3007440e7900c1f57ce78c6f4d6986f` on `research/igm-rate-export-followup-20261008`.
- The characteristic and every internal segment now consume canonical `Tracked` photon stock. Number, energy, inherited loss, source convolution, A/B owners, redshift loss and positive photoheat remain paired when binary64 readout becomes zero.
- The saved V3 endpoint energy discrepancy is not overwritten. `reconcile_node_energy` reconstructs the exact node energy for the current eta/epoch and adds the prior energy loss plus the extended-range absolute discrepancy to the carried U loss; the paired kernel propagates it through U/red/B. The direct positive heat owner remains an independent N/source reconstruction, so the same U discrepancy is not charged there a second time.
- The former coarse k17 blocker now accepts. The matched common state coarse k17 / fine k34 / tail k17 passes the unchanged 37-field, source N/E and loss-budget comparisons.
- The remaining 0.0008 suffix completed without rerunning the accepted prefix: coarse k17 to k48, fine k34 to k96 and tail k17 to k48. The final common epoch is `s=-2.564149357461537`, `z=11.98960415889089`.
- Final comparison: temporal maximum allowance ratio `0.023932797389989293`, tail maximum `4.080871757717751e-12`; maximum suffix source ratio `0.21071655885039875`.
- Accepted-record replay now restores the final canonical N/E or outflow pair before comparison and applies the durable scalar-to-ledger order map. A live two-transition capture/replay passed.
- Original checkpoints, historical failures, PR85 log-tail and PR86 canonical Wide sources remain unchanged. New calculation artifacts are confined to `repair_20261008/runs`.
- The 0.0008 manufactured-model discrete refinement is accepted. Later horizons through z=10, continuum error authority and physical admission remain incomplete/HOLD.
