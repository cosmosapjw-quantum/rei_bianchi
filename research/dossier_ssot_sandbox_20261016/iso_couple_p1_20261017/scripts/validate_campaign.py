#!/usr/bin/env python3
import csv, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
rows=list(csv.DictReader((ROOT/'evidence/convergence_campaign.csv').open()))
assert len(rows)==36
x=[{k:float(v) for k,v in row.items()} for row in rows]
levels=(1e-5,1e-7,1e-9)
err={str(t): max(r['relative_extent_to_strict'] for r in x if r['rtol']==t) for t in levels}
assert err[str(1e-9)]<err[str(1e-7)]<err[str(1e-5)]
assert max(abs(r['baryon_difference_m3']) for r in x)==0
assert max(abs(r['electron_difference_m3']) for r in x)==0
assert max(abs(r['delta_u_chem_J_m3']+r['delta_u_th_J_m3']) for r in x)==0
src=list(csv.DictReader((ROOT/'evidence/savin_detailed_balance_diagnostic.csv').open()))
y=[r for r in src if float(r['temperature_K'])==10000.0][0]
assert float(y['kf_over_kr_savin'])>1.0
assert float(y['expected_exp_minus_42p915_over_T'])<1.0
print('PASS_36_BOUNDED_ROWS_MASS_ELECTRON_ENERGY_AND_STRICT_REFINEMENT',err)
