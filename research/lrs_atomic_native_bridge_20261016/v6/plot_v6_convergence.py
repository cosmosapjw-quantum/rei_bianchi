"""Produce a simple monotone high-density error-convergence figure."""
from __future__ import annotations
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

p=Path(__file__).resolve().parent
D=json.loads((p/'dense_multichannel_v6.json').read_text())['data']
fig,ax=plt.subplots(figsize=(8,5.2))
for name,result in D.items():
    dt=[r['h'] for r in result['rows']]
    old=[r['old_T_error'] for r in result['rows']]
    new=[r['new_T_error'] for r in result['rows']]
    ax.loglog(dt,old,marker='x',linestyle='--',label=f'{name}: frozen-T V5')
    ax.loglog(dt,new,marker='o',linestyle='-',label=f'{name}: midpoint V6')
ax.set_xlabel(r'Maximum step $\Delta X$')
ax.set_ylabel('Final gas-temperature error (K)')
ax.set_title('Source-backed Grackle Case-A dense recombination: Radau comparison')
ax.legend(fontsize=8,ncol=2)
ax.grid(True,which='both',alpha=.3)
fig.tight_layout()
fig.savefig(p/'dense_order_v6.png',dpi=150)
plt.close(fig)
