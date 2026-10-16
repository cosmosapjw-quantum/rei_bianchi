"""Stiff-regime refinement falsification: positivity != uniform 2nd order."""
from __future__ import annotations
import json
from math import log2
from pathlib import Path
from rrdr_sourcefree_v8 import evolve,radau_reference,compare

root=Path(__file__).resolve().parent
D=1e6;L=1e-4
ref=radau_reference(x_end=L,density_factor=D)
rows=[]
for n in (8,16,32,64,128,256,512,1024):
    r=evolve(n,x_end=L,density_factor=D)
    metrics=compare(r,ref)
    assert r.min_temperature>=10000 and r.max_temperature<=24000
    assert abs(r.energy_residual)<1e-24
    row={'n':n,'h':L/n,'Tgas_K':r.temperature,**metrics}
    rows.append(row)
for i in range(1,len(rows)):
    rows[i]['order_from_previous']=log2(rows[i-1]['T_error_K']/rows[i]['T_error_K'])
assert rows[1]['order_from_previous'] < 0
assert rows[-1]['order_from_previous'] >1.95
result={'case':'fixed-background-comoving-atomic-density-factor=1e6 (NOT physical cosmology)',
        'original_native_owner':'6ea2b1b4b3875c9163cafc45efe720afded43fc4',
        'stiff_limit':'large DeltaX*(ne alpha/H) not uniformly second-order at coarse steps',
        'positivity_energy':'PASS all tested steps','uniform_stiff_order':'NOT_ESTABLISHED',
        'rows':rows}
(root/'evidence/C8_STIFF.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
for row in rows:print(f"n={row['n']:<5d} T_err_K={row['T_error_K']:.9g} exp={row['max_rr_exposure']:.5g} order={row.get('order_from_previous','-')}")
