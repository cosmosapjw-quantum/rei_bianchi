#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
HERE=Path(__file__).resolve().parent;STAGE=HERE.parent;PLOTS=STAGE/'plots';PLOTS.mkdir(exist_ok=True)
three=json.loads((STAGE/'data/THREE_LANE_INTERVAL_MAP.json').read_text())
part=json.loads((STAGE/'data/PARTITION_SENSITIVITY.json').read_text())
keys=('x_HII','x_HeII','x_HeIII','log_T')
labels=(r'$\Delta x_{\rm HII}$',r'$\Delta x_{\rm HeII}$',r'$\Delta x_{\rm HeIII}$',r'$\Delta\ln T$')
# 1. Public widths against gate.
values=[three['max_widths'][k] for k in keys];gate=2e-3
fig,ax=plt.subplots(figsize=(7.2,4.6));x=np.arange(len(keys));ax.bar(x,values);ax.axhline(gate,linestyle='--',label=r'public gate $2\times10^{-3}$');ax.set_yscale('log');ax.set_xticks(x,labels);ax.set_ylabel('validated maximum width');ax.set_title('Four-site validated widths versus public gate');ax.legend();fig.tight_layout();fig.savefig(PLOTS/'validated_widths_vs_gate.png',dpi=220);plt.close(fig)
# 2. Partition sensitivity.
parts=np.array([r['partition'] for r in part['rows']],float)
fig,ax=plt.subplots(figsize=(7.2,4.8))
for key,label in zip(keys,labels):ax.plot(parts,[r['widths'][key] for r in part['rows']],marker='o',label=label)
ax.axhline(gate,linestyle='--',label='public gate');ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_xlabel('partition count');ax.set_ylabel('validated width');ax.set_title('Refinement sensitivity of validated enclosure');ax.legend(ncol=2);fig.tight_layout();fig.savefig(PLOTS/'partition_sensitivity.png',dpi=220);plt.close(fig)
# 3. Local implicit certificate margins.
diag=three['rows'][0]['diagnostics'];names=[];vals=[]
for half in ('first_half','second_half'):
 d=diag[half]
 for key,label in (('predictor_row_sum','predictor'),('gamma_row_sum',r'$\gamma$ stage'),('corrector_row_sum','corrector')):
  names.append(f"{half.replace('_',' ')}\n{label}");vals.append(d[key])
fig,ax=plt.subplots(figsize=(8.0,4.6));ax.bar(np.arange(len(vals)),vals);ax.axhline(1.0,linestyle='--',label='Krawczyk contraction limit');ax.set_yscale('log');ax.set_xticks(np.arange(len(vals)),names);ax.set_ylabel('maximum row-sum bound');ax.set_title('Local MPRK Krawczyk margins');ax.legend();fig.tight_layout();fig.savefig(PLOTS/'local_krawczyk_margins.png',dpi=220);plt.close(fig)
# 4. Event distance relative to temperature enclosure width.
rows=part['rows'];dist=np.array([r['table_event']['minimum_distance'] for r in rows]);tw=np.array([r['widths']['log_T'] for r in rows])
fig,ax=plt.subplots(figsize=(7.2,4.6));ax.plot(parts,dist,marker='o',label='nearest knot distance');ax.plot(parts,tw,marker='s',label=r'$\Delta\ln T$ enclosure width');ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_xlabel('partition count');ax.set_ylabel(r'distance in $\ln T$');ax.set_title('Hummer–Seaton topology-event clearance');ax.legend();fig.tight_layout();fig.savefig(PLOTS/'table_event_clearance.png',dpi=220);plt.close(fig)

# 5. Set-valued full-versus-two-half local-error bound.
local=np.array([r['maximum_validated_local_error'] for r in rows])
local_gate=2e-4
fig,ax=plt.subplots(figsize=(7.2,4.6));ax.plot(parts,local,marker='o',label='validated local-error bound');ax.axhline(local_gate,linestyle='--',label=r'acceptance gate $2\times10^{-4}$');ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_xlabel('partition count');ax.set_ylabel('maximum blockwise error bound');ax.set_title('Full-step versus two-half-step validated error');ax.legend();fig.tight_layout();fig.savefig(PLOTS/'validated_local_error.png',dpi=220);plt.close(fig)

summary={'maximum_width':max(values),'gate':gate,'gate_to_max_width_ratio':gate/max(values),'maximum_krawczyk_row_sum':max(vals),'minimum_table_clearance_ratio':float(np.min(dist/tw)),'maximum_validated_local_error_partition_2048':float(local[1]),'local_error_gate':local_gate,'local_error_gate_ratio_partition_2048':float(local_gate/local[1]),'partition_acceptance':{str(int(r['partition'])):bool(r['certified']) for r in rows},'plots':[p.name for p in sorted(PLOTS.glob('*.png'))]}
(STAGE/'data/PLOT_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
print(json.dumps(summary,indent=2,sort_keys=True))
