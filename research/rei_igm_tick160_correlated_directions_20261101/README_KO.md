# REI IGM 26-event real-parent finite-direction stress, original tick 160→161

This Draft/HOLD experiment **reuses original 46,080-node 26-event MPRK22(1)/Alexander SDIRK2 source** at `[160,161]`. It evaluates full vs two half for nine nuclei-conserving marginal-box candidates along four global input directions, separately for three original lanes. The experiment is **not** a rigorous nonlinear `D_h(X,theta)` enclosure of the whole accepted parent; `28/88` canonical unchanged.

Execution on the immutable PR #328 lineage via GitHub Actions `rei-igm-real-26event-directions.yml`. The source archive and kernel are both SHA-locked, and failures are retained. No production, no merge, no tolerance change, no auto-next.

```
python -m unittest discover -s research/rei_igm_tick160_correlated_directions_20261101 -p 'test_*.py' -v
python research/rei_igm_tick160_correlated_directions_20261101/directional_probe.py --repo . --lane LOCAL_NEUTRAL_HAZARD_PRIMARY --output experiment/PRIMARY
```

Results are written as `REAL_26EVENT_PARENT_DIRECTIONS_<lane>.csv.gz` plus `RESULT.json`. The zipped GitHub Actions artifacts are not an indefinite external dual-provider backup. Source-owner 26-event kernel, historical original state, and prior PRs remain immutable.

See `SCIENTIFIC_CONTRACT_KO.md` for equations, rigor boundary, and `ADVERSARIAL_REVIEW_KO.md` for falsification/claim controls. `STAGE_PROGRESS.json` is a single evidence ledger for R/C research phases, not 20 independent experiments.
