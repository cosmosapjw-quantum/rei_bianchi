# Isolated thermal H/D charge exchange

`thermal_cx.py` integrates one normalized extent at fixed proper volume with temperature-dependent Savin rates or an explicitly named custom provider. Densities use cm^-3, thermal inventory eV cm^-3, defect eV, rates cm^3/s, time s and temperature K. Pure H/D neutrality supplies electrons; no spectator inventory is accepted.

The runtime uses Python stdlib only. Read `CONTRACT.json`, `THEORY.md`, `CODING.md` and `evidence/C9_INDEPENDENT_REVIEW.json` for equations, acceptance and reviewed scope. C6/C7 evidence is complete and should be reused; running the harness again requires a new output path so saved evidence remains intact. The independent probe is cached and must not be replayed as routine verification.

API: `integrate(State(...), Defect(delta_chi_eV, source), RateProvider(...), t_requested_s, Controls(...))`. `SAVIN2002` retains its inclusive 2.7–200000 K domain. Return fields distinguish full completion from provider approach, work caps, underflow and arithmetic failure. The supplied dataclasses are immutable.

CLI: `python3 thermal_cx.py --input INPUT.json --output OUTPUT.json`. Input is `{ "state": { "h0": ..., "hp": ..., "d0": ..., "dp": ..., "thermal_eV_cm3": ... }, "defect": { "delta_chi_eV": ..., "source": "..." }, "t_requested_s": ..., "controls": {} }`. The CLI selects Savin2002, returns exit0 for complete intervals and exit2 for incomplete/invalid results. API and JSON evidence were exercised; CLI was parsed but not executed.

`CONVERGENCE.png` and `.svg` come only from saved C7 arrays through `plot_convergence.py`; no solver run was added for plotting. This is a synthetic isolated-component result, with standalone PASS_SCOPED and no cosmological-history admission. See `REPORT_KO.md` and `NEXT_DAG.json` for results and next work. Use publisher-owned `FINAL_PUBLICATION.json` for exact unit-only C10 archive pins and backup receipts.
