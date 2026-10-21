# Selective component and z2 implementation

`unified_pilot.py` imports the recovered `adapter.py`, `component_adapter.py`, `resources.py`, and `pilot.py`. The persistent cooperative `run` supervisor is mechanically copied from recovered `pilot.py`; physical RHS, quadrature, caches, solver, and tolerances remain imported unchanged. Changes provide phase manifests, exact35 raw/input/receipt references, historical B1 debit, independent B2 envelope, fixed checkpoint paths, raw-hash resume verification, explicit bounded memory/disk deferral, per-case scientific dispatch, and operation receipts. Only the controller's own workers may be stopped.

B1 uses the existing component adapter calibration and121-point gates. B2 reconstructs each exact prefix configuration and changes only frozen SourceLock.aend to1/3 to extend the fields domain. The whole40/56-vector saved endpoint is the initial tail state, including elapsed-time and metric fields. The original source a_ref, Href, cosmology, saved amplitudes and all quadratures are retained. A33-point tail includes the exact saved join and32 points are appended. Every original diagnostic prefix is also reused exactly; new component diagnostics are additive. B2 gates explicitly test153points, exact prefix/join, z2, number, packet populations, energies, brightness, component identities and actual isotropy. Existing original.validate hardcoded121/a=.2 gates are not used on the tail.

No retry flag exists. A noncompleted attempt stays nonpending. Fixed phase output paths prevent directory-level budget resets. Case ATTEMPT charges are supervisor dispatch-to-observation walls, preserving startup/queue/observation overhead. Controller operations include process startup before numerical imports, and plan/check/plot receipts debit the appropriate controller envelope. The14 static changed-risk checks in MECHANICAL_TEST.json do not call solve_ivp. Recovered raw and executed-source identities remain historical.

Commands, from the package root:

```bash
python3 components/unified_pilot.py run --phase b1 --profile sandbox --max-workers 4 --review-approval /absolute/path/PHYS_MATH_CONTRACT_REVIEW.json
python3 components/unified_pilot.py check --phase b1
python3 components/unified_pilot.py run --phase b2 --profile sandbox --max-workers 4 --review-approval /absolute/path/PHYS_MATH_CONTRACT_REVIEW.json
python3 components/unified_pilot.py check --phase b2
python3 components/plot_extension.py
```

Resume adds `--resume`; completed raw is rehashed and retained. `z2_extension/run_ncp.sh` prepares the same fixed checkpoints with the NCP resource profile and max63 workers; this is not an NCP execution receipt.
