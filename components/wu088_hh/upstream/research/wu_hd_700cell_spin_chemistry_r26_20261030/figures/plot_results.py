"""R26 source-based figures. Diagnostics only, no observed cosmic yields or Q."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decimal import Decimal
from src.native_atlas import TEMPS,INITIAL,FINAL,parse_printed

ROOT=Path(__file__).resolve().parents[1]
source=json.loads((ROOT/'sources/GL2022_700_SOURCE.json').read_text())
atlas=json.loads((ROOT/'results/GL2022_700_ATLAS.json').read_text())
study=json.loads((ROOT/'results/MULTI_J_SPIN_ORDER_MEMORY.json').read_text())

# Source-native rate rows J0..J6, source-suspect J5 excluded and explicitly labelled.
fig,ax=plt.subplots(figsize=(7.2,4.2))
for T in (105,255):
    vals=[]
    for j in INITIAL:
        row=next(q for q in atlas['rows'] if q['T_K']==T and q['HD_J']==j and q['policy']=='raw_SQM')
        vals.append(float(row['positive_sum_cm3_s']) if row['source_status']=='PASS_PRINTED_COMPLETE' else np.nan)
    ax.plot(list(INITIAL), vals, marker='o',label=f'Raw SQM, {T} K')
ax.set_xlabel('Initial HD rotational J')
ax.set_ylabel('Sum of printed J′=0…9 rates [cm³ s⁻¹]')
ax.set_yscale('log');ax.set_xticks(list(INITIAL));ax.legend(fontsize=8)
ax.set_title('GL2022 original SQM rates, j=5 source-held')
fig.tight_layout();fig.savefig(ROOT/'figures/SOURCE_700_INITIAL_J.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.0,4.0))
policies=[('raw','Raw SQM'),('eq_spin','Eq. (6–7) spin weighted')]
diff=[float(study[k]['delta_forward_minus_reverse_extent_m3']) for k,_ in policies]
ax.bar([0,1],diff,width=.48)
ax.set_xticks([0,1],[label for _,label in policies]);ax.set_ylabel('Extent(105→255) − Extent(255→105) [m⁻³]')
ax.axhline(0,color='black',linewidth=.7)
for i,v in enumerate(diff):ax.annotate(f'{v:,.1f}',(i,v),xytext=(0,7),textcoords='offset points',ha='center',va='bottom')
ax.set_ylim(min(diff)*1.3,500)
ax.set_title('Temperature-order memory: source-conditional 2-J kinetics')
fig.tight_layout();fig.savefig(ROOT/'figures/ORDER_MEMORY_TWO_POLICY.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.4,4.1))
toks=source['tokens_jprime_j_T'][7][3]
vals=[float(parse_printed(v)) if parse_printed(v) is not None else np.nan for v in toks]
ax.semilogy(TEMPS[5:],vals[5:],'o-',label='Published literal J=3 → J′=7')
ax.scatter([2505],[vals[8]],s=120,marker='x',label='Source-suspect 6.72(16)')
ax.set_xlabel('Temperature [K]');ax.set_ylabel('Published SQM rate [cm³ s⁻¹]')
ax.set_title('Original Table 8: 2505 K exponent anomaly (1005–3005 K)')
ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'figures/TABLE8_SOURCE_EXPONENT_AUDIT.png',dpi=180);plt.close(fig)
