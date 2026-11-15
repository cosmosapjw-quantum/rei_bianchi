# Original AXBI approximation-validity package

The authoritative result is `results/FULL_SUMMARY.json`, derived from all 1,248,952 saved native rows for the four original completed cases. `DERIVATION_AND_RESULT.md` defines the physics, source reuse, numerical checks, and limits. `results/SUMMARY.json` is the superseded background-only reduced-history cross-check. No new physical trajectory was integrated in this package.

`INPUT_MANIFEST_ORIGINAL_FOUR.json` and `SOURCE_ARCHIVE_MANIFEST.json` pin the original four-case input bytes; large histories and the source archive are not included. The original scenario is copied without changes into `ORIGINAL_SCENARIO_LOCK.json`.

From this directory, with the private native inputs available in directories `CASE/history.csv`:

```sh
python full_history_diagnostic.py --inputs /absolute/path/to/source_full/private_inputs --out /absolute/path/to/reproduction_output
python -m unittest -v test_background_stress.py
```

The review files under `reviews/` are byte-for-byte mirrors of the independent review. Their `axbi_science/...` reviewed paths refer to this package root; original `rei_current/research/rei_axbi_owner_loop_20261115/...` references identify the owner sources. The archived independent check script retains its historical workspace layout and is preserved as executed evidence. Its separate adaptive angular and proper-time results are in `reviews/AXBI_INDEPENDENT_NUMERICS.json`.

Admission is limited to the four represented saved-history approximation diagnostics. It does not close parent AX03/AX08, optional-observable AX10, AX11 convergence, AX12 robustness, or any abundance/temperature error bound. C9 links the completed independent review. C10 remains pending the parent's actual integration/publication receipt.
