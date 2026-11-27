"""Produce two clearly scoped exploratory diagnostics. No solver or data mutation."""
import json
from pathlib import Path
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
RESULTS=ROOT/'results'
with (RESULTS/'C1_SECOND_CELL_PILOT_FINAL.json').open() as f: warm=json.load(f)
with (RESULTS/'C1_REI_SIGNED_PARITY.json').open() as f: signed=json.load(f)
fig,ax=plt.subplots(figsize=(8.5,5.2))
for label in ('PL','HERMITE'):
 rows=[x for x in warm['data'] if x['kind']==label]
 ax.plot([r['u'] for r in rows], [r['max_scaled_gas_residual_s_inv'] for r in rows],marker='o',label=label)
ax.set_yscale('log')
ax.set_xlabel('Second saved-cell fractional proper time u')
ax.set_ylabel('Maximum scaled gas RHS residual (1/s)')
ax.set_title('Warm P01 cell 2: sampled residual, NOT a whole-cell bound')
ax.legend()
fig.tight_layout();fig.savefig(RESULTS/'HE18_C1_second_cell_residual.png',dpi=165);plt.close(fig)

fig,ax=plt.subplots(figsize=(8.5,5.2))
from decimal import Decimal
for field in ('x_HII','x_HeII','electron'):
 values=signed['observables'][field]
 xs=[0.0,.005**2,.01**2]
 ys=[0.0,float(Decimal(values['even_half_q'])),float(Decimal(values['even_full_q']))]
 ax.plot(xs,ys,marker='o',label=field)
ax.set_xlabel('q_ref² at fixed stored scale factor')
ax.set_ylabel('Even response of displayed partial history')
ax.set_title('AXBI 5-case partial endpoint: exploratory even-shear response')
ax.legend()
fig.tight_layout();fig.savefig(RESULTS/'HE18_C1_REI_partial_even_response.png',dpi=165);plt.close(fig)
