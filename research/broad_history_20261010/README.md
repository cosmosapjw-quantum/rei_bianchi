# Broad-history reduced reionization lane

Start with `REPORT_KO.md`, `SCIENTIFIC_CONTRACT.md` and `RESUME.json`.
This opt-in Python module does not change any Rust production default.

Dependencies: Python3.12, NumPy2.3.5, SciPy1.17.0, matplotlib; pytest9.1.1 only for focused tests. Exact used versions appear in run records. Published equations are independently implemented here; the existing repository Bianchi background is imported with an exact SHA256 pin. No external copyrighted PDF contents are redistributed.

From repository root:

```bash
python3 -m pytest research/broad_history_20261010/tests -q
python3 research/broad_history_20261010/run_campaign.py --output research/broad_history_20261010/evidence/NEW_RUN --fine-steps 16384
```

The campaign always covers mean-volume z20→4. New output directories avoid replacing completed evidence. Repeating the same command resumes only matching completed case identities and NPZ hashes. The full backup contains RUN001/002 NPZ trajectories; the Git projection contains source, compact traces, run records, comparison results and figures. To resume a saved run without recomputation, restore its NPZ files from the named checkpoint archive first. `validate_campaign.py` is the original validation entry for the full restored RUN002, not a promise that compact Git projection alone contains every raw array.

`reference.py` independently transcribes the same published closure and uses DOP853/events. It supplies a numerical comparison, not an independent physical theory. Its original command writes its standard evidence filenames; use a copied workspace for a fresh optional replay, preserving old source/evidence identities.

`evidence/RUN001/CAMPAIGN.json` is a retained convergence FAIL. RUN002 increased resolution without changing tolerances. `independent/DECISION.json` limits admission to this reduced model.

Photon budget and partial tau have explicit closures. CR/RCT/HH and thermal-history completion remain open. Existing original research is preserved in `BLOCKERS.json` and source-pinned repo returns; no original plan is deleted.
