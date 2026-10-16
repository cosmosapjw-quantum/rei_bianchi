"""Rebuild nonauthoritative per-case views from the byte-locked merged C8 data.

The archived aggregated original 144 rows remain the authority. This script creates
three deterministic *derived views* for merge_study.py; no new integration occurs.
"""
from __future__ import annotations
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
E = BASE / 'evidence'
obj = json.loads((E / 'C8_MATRIX_144.json').read_text())
summ = json.loads((E / 'C8_SUMMARY.json').read_text())
assert len(obj['rows']) == 144 and len(obj['summary']) == 24
for case in obj['cases']:
    rows = [r for r in obj['rows'] if r['case'] == case]
    entries = [s for s in obj['summary'] if s['case'] == case]
    assert len(rows) == 48 and len(entries) == 8
    view = {'schema':'rei.v11.c8.thermclock.regenerated-view.1',
            'source':'DERIVED_AGGREGATE_NO_NEW_SOLVE',
            'grackle_literal_table':summ['grackle_original_literal_C_table'],
            'modes':summ['methods'], 'step_grids':summ['steps'],
            'rows':rows, 'summary':entries}
    p = E / f'C8_MATRIX_{case}.json'
    p.write_text(json.dumps(view, ensure_ascii=False, indent=2,sort_keys=True)+'\n')
    print('DERIVED_CASE_VIEW',case,len(rows))
