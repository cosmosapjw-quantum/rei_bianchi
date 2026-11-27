"""Plot only measured-as-printed GL2022 SQM source channels and conditional model."""
from pathlib import Path
import sys, json
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
a=json.loads((ROOT/'results/BRANCHING_NATIVE_R25.json').read_text())
h=json.loads((ROOT/'results/TWO_SEGMENT_PRODUCT_HISTORY.json').read_text())
T=[r['T_K'] for r in a['data'][1:]]
f1=[100*float(r['branch_fraction_J_conditional'][1]) for r in a['data'][1:]]
fo=[100*float(r['ortho_fraction_J_odd_conditional']) for r in a['data'][1:]]
fig,ax=plt.subplots(figsize=(7.6,4.5))
ax.plot(T,f1,'o-',label="H2 J'=1 among reported")
ax.plot(T,fo,'s--',label="H2 odd J' among reported")
ax.set_xscale('log');ax.set_xlabel('Source temperature T [K]');ax.set_ylabel('Conditional reported branching [%]')
ax.set_ylim(0,75);ax.grid(True,alpha=.25);ax.legend(loc='upper right',frameon=False)
ax.set_title('GL2022 H+ + HD(v0,J2): original SQM product channels')
fig.tight_layout();fig.savefig(ROOT/'figures/BRANCHING_FROM_SOURCE.png',dpi=200);plt.close(fig)

from src.state_branching import piecewise_equal_reactants
from decimal import Decimal
src=json.loads((ROOT/'sources/GL2022_NATIVE_PRODUCT_GRID_R25.json').read_text())
rev=piecewise_equal_reactants(src,n0_m3=Decimal('1e6'),schedule=((255,Decimal('5e9')),(105,Decimal('5e9'))))
y1=np.array([float(x) for x in h['end_H2_v0J0_to_J9_m3']])
y2=np.array([float(x) for x in rev['end_H2_v0J0_to_J9_m3']])
js=np.arange(6)
fig,ax=plt.subplots(figsize=(7.6,4.4));width=.38
ax.bar(js-width/2,y1[:6]/1e3,width,label='105 K then 255 K')
ax.bar(js+width/2,y2[:6]/1e3,width,label='255 K then 105 K')
ax.set_yscale('symlog',linthresh=.01)
ax.set_xlabel("Final H2 rotational state J' (subset 0..5)")
ax.set_ylabel('Conditional generated H2 [10³ m⁻³]')
ax.set_title('Equal total extent, different product-state memory')
ax.set_xticks(js);ax.legend(frameon=False);ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(ROOT/'figures/PRODUCT_ORDER_MEMORY.png',dpi=200);plt.close(fig)
print('source branching+order-memory figures generated')
