# BASS_HE E13C9 — local signed Volterra correction

Decision: **PROMOTE_SCOPED_LOCAL_SIGNED_VOLTERRA** on five captured OFF paths / twelve segments. All 170 raw intervals are nested and nonincreasing. Selected weighted P/H widths decrease 32.5711822283% / 30.4812007649%. E13C8 full finite admission is unchanged; full-population second correction is NOT_RUN; physical/continuum/production/receiver HOLD. New NCP jobs: **0**.

Start with [REPORT_KO.md](REPORT_KO.md), [CURRENT_STATE.json](CURRENT_STATE.json), and [independent decision](review/independent/INDEPENDENT_DECISION.json). The scientific contract and exact selected result pins are [SCIENTIFIC_CONTRACT.md](SCIENTIFIC_CONTRACT.md) and [SELECTED_CANDIDATE.json](analysis/ACTUAL_PORTABLE/SELECTED_CANDIDATE.json).

The method reuses original N512/N1024 first-variation enclosures at P60, computes only new causal prefixes and signed corrections at M128 (M256 for node1162), and propagates new incoming uncertainty and original signed seams. [Code](code/signed_volterra.py) and [derivation](theory/SIGNED_PREFIX_DESIGN.md) are included.

The complete archive contains all raw evidence, original E13C8 complete backup, and its recovery kit. The Git projection keeps source, contract, summaries, review and byte inventories; larger raw numerical evidence is in that complete archive. [Reproduction](REPRODUCIBILITY.md) distinguishes inspection/recovery from completed scientific work. Do not rerun completed baselines or dispatch a new bulk job from this package.
