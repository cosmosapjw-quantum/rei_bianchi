# REI F4 PR299/PR300 terminal-electron + HHe thermal/clock crosswalk

One bounded source-backed physical-fast auxiliary. Original archives: PR298 source, PR299 tangency, PR300 FS2010 threshold, nested PR297 causal source. This package retains only the **four exact source CSVs necessary for replay**, rather than duplicating ~126 MB of immutable parent source-inclusive ZIPs already double-backed. Their original parent ZIP byte hashes and Git heads are pinned in SOURCE_LOCK.json; all four included CSVs are independently SHA256 verified. No original PR changed.

For a clean replay on Linux with Python, numpy, pandas, matplotlib:

```sh
bash VERIFY.sh
```

Outputs: `results/CROSS_OWNER_TERMINAL_THERMAL_192.csv`, `results/SCIENCE_RESULTS.json`, 6 PNG scientific plots. Verification checks SHA manifests, 19 physical tests, source correspondence, deterministic numerical outputs and PNGs under the same rendering environment.

This is NOT a REI17 full-native common F/J or an evolved thermal history. No new IVP, no true gas heating, τ or CMB. The three different energy bounds are *different physics claims*, not interchangeable.

Working 33/88; Central 28/88; Physical Fast 4/7; F4 PARTIAL; Production HOLD. Stage ledger entries are retrospective milestones for one bounded execution, not 20 independently executed source experiments. Native subagent tool unavailable, distinct-author R6/C9 NOT_RUN.