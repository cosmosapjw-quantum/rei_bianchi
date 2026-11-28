#!/usr/bin/env python3
"""Plot certified enclosures; endpoints are data bounds, not confidence limits."""
from pathlib import Path
import json
import hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

here = Path(__file__).resolve().parent
root = here.parent
source = root/'checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json'
d = json.loads(source.read_text())
rows = [('Total endpoint difference', d['DeltaT_K_after_endpoint_intersection'])]
names = [('stock_backward_euler','Stock: backward Euler'),('opacity_change','Opacity change'),('gas_movement','Gas state movement'),('source_time','Source time'),('stock_intermediate_redshift','Stock: intermediate redshift'),('remap_composition','Remap composition'),('absorption_transport_commutator','Absorption / transport order')]
for key,label in names:
    rows.append((label,d['sectors'][key]['temperature_K_after_intersection']))
rows += [('Birth: backward Euler',d['birth_signed_factorization']['birth_backward_euler_all_b_0_1_K']),('Birth: redshift',d['birth_signed_factorization']['birth_redshift_all_b_0_1_K'])]
fig,ax=plt.subplots(figsize=(7.7,4.7),layout='constrained')
for index,(label,v) in enumerate(rows):
    lo,hi=[1000*float(x) for x in v['outward_decimal']]
    color='#185A89' if hi<=0 else '#B66220' if lo>=0 else '#6E747C'
    y=len(rows)-1-index
    ax.plot([lo,hi],[y,y],color=color,lw=5 if index==0 else 3,solid_capstyle='butt')
    ax.plot([lo,hi],[y,y],'|',color=color,ms=10,mew=1.2)
ax.axvline(0,color='#50555B',lw=.9,zorder=0)
ax.axhline(len(rows)-1.55,color='#BBC2C8',lw=.7)
ax.set_yticks(range(len(rows)),[r[0] for r in reversed(rows)],fontsize=9)
ax.set_xlabel(r'Temperature difference / contribution, $T_2-T_F$ (mK)',fontsize=10)
ax.set_xlim(-1.70,.16)
ax.grid(axis='x',color='#E1E6EA',lw=.6)
ax.set_axisbelow(True)
ax.spines[['top','right','left']].set_visible(False)
ax.tick_params(axis='y',length=0)
ax.legend(handles=[Line2D([0],[0],color='#185A89',lw=3,label='Nonpositive'),Line2D([0],[0],color='#B66220',lw=3,label='Nonnegative'),Line2D([0],[0],color='#6E747C',lw=3,label='Sign unresolved')],loc='lower left',fontsize=8,frameon=False)
fig.savefig(here/'temperature_sectors.pdf')
fig.savefig(here/'temperature_sectors.png',dpi=180)
plt.close(fig)
(here/'FIGURE_PROVENANCE.json').write_text(json.dumps({'input':str(source.relative_to(root)),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'visualization':'Deterministic outward enclosures, converted to mK for display only. Numeric proof retains exact rational endpoints.','scope':'Same linked global lambda,b in [0,1]^2. Birth rows include b=0 and use sign-preserving factorizations.','files':['temperature_sectors.pdf','temperature_sectors.png']},indent=2)+'\n')
