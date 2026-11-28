"""Read frozen primary printed values; figures are *illustration*, not extra observations."""
from pathlib import Path
from decimal import Decimal
import json
import numpy as np
import matplotlib.pyplot as plt

ROOT=Path(__file__).parents[1]
rows=json.loads((ROOT/'results/PRIMARY.json').read_text())['rows']
T=np.asarray([int(r['T_K']) for r in rows],dtype=float)
K=np.asarray([float(Decimal(r['SQM_printed_1e-10_cm3_s'].split('/')[0])/Decimal(r['SQM_printed_1e-10_cm3_s'].split('/')[1])) if '/' in r['SQM_printed_1e-10_cm3_s'] else float(r['SQM_printed_1e-10_cm3_s']) for r in rows])
O=np.array([1.1,1.7]); H=np.array([0.2,0.2]);tf=np.linspace(150,350,200)
fig,ax=plt.subplots(figsize=(7.2,4.05));
ax.plot(tf,8.57*np.exp(-405/tf),label='Authors\' global Arrhenius fit (not state-resolved)')
ax.scatter(T,K,marker='D',s=65,label='Printed SQM thermal TOTAL (two points)')
ax.errorbar(T,O,yerr=H,fmt='o',capsize=4,linewidth=1.3,label='Experiment, reported ±0.2 (type unspecified)')
ax.set_xlabel('Temperature (K)');ax.set_ylabel(r'Total reactive rate ($10^{-10}$ cm$^3$ s$^{-1}$)')
ax.set_title(r'H$^+$ + HD $\rightarrow$ D$^+$ + H$_2$: printed thermal totals');ax.legend(fontsize=8,loc='upper left');ax.grid(alpha=0.25);fig.tight_layout();
fig.savefig(ROOT/'figures/GL2022_PRINTED_TOTAL_RATE.png',dpi=180);fig.savefig(ROOT/'figures/GL2022_PRINTED_TOTAL_RATE.svg');plt.close(fig)
fig,ax=plt.subplots(figsize=(6.5,3.7));zs=np.asarray([.55,2.55]);ax.bar([str(int(t)) for t in T],zs,width=.45)
for i,z in enumerate(zs):ax.text(i,z+0.07,f'{z:.2f}',ha='center',fontsize=10)
ax.axhline(1,linestyle='--',label='One *printed* ±0.2 halfwidth (not 1σ)')
ax.set_ylim(0,3.15);ax.set_xlabel('Temperature (K)');ax.set_ylabel('SQM − experimental center / printed ±0.2')
ax.set_title('Descriptive differences, not significance or confidence');ax.legend(fontsize=8,loc='upper left');ax.grid(axis='y',alpha=.2);fig.tight_layout();
fig.savefig(ROOT/'figures/GL2022_PRINTED_HALF_WIDTH.png',dpi=180);fig.savefig(ROOT/'figures/GL2022_PRINTED_HALF_WIDTH.svg');plt.close(fig)
print('saved: 2 PNG + 2 SVG; source: already saved PRIMARY.json')
