# Actual full-stage progress snapshot — incomplete

Captured UTC: 2026-10-14T08:33:57.015706+00:00

- ZERO: checkpointed z̄20 → 12.78675633; elapsed 157.13667564 Myr; 135480 accepted, 406494 tentative, 2845482 RHS.
- SHEAR_PLUS: checkpointed z̄20 → 14.02019975; elapsed 116.63122144 Myr; 108060 accepted, 324234 tentative, 2269662 RHS.

The target z̄4 is not reached. Snapshots are exact complete CSV prefixes bounded by the captured atomic checkpoint; source identities, capture timestamps, prefix sizes/hashes and excluded incomplete tails are in SNAPSHOT_MANIFEST.json. Different case cutoffs are not a matched comparison. No full AX14 completion, global numerical refinement, resolved shear response or validated tiny-trace precision is claimed. Electrons are labelled charge census and excluded from nuclear baryon inventory. Time/Tgas plots preserve original time order; exact zeros are masked only on the log display.

![Elapsed-time progress](progress_abundance_vs_elapsed_time.png)

![Time-ordered Tgas progress](progress_abundance_vs_Tgas_time_ordered.png)

Reproduce figures with `python3 snapshot_progress.py --render snapshot_20261014T083357015083Z` from this postprocessor directory; no live source is reread. Continue the existing supervisor and checkpoint identities; do not relaunch completed or running cases.
