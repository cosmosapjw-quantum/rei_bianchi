import os
import tempfile
os.environ['MPLCONFIGDIR']=tempfile.mkdtemp(prefix='transport-mplconfig-')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
from pathlib import Path
R=Path(__file__).resolve().parent
S=json.loads((R/'SUMMARY.json').read_text());cases={x['method']:x for x in S['cases']if x['n']==256}
methods=['stock','partial','fv','dg','dg_limited'];labels=['Whole-node\nstock','Partial-cell\nP0','Physical-E\nFV P0','DG P1\nunlimited','DG P1\nlimited'];colors=['#6d7785','#0c817e','#d48117','#a74c89','#386cb0']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,(a,b)=plt.subplots(1,2,figsize=(11,5.25),gridspec_kw={'width_ratios':[1,1]})
fig.subplots_adjust(left=.078,right=.98,bottom=.25,top=.77,wspace=.29)
for i,(m,col)in enumerate(zip(methods,colors)):
 e=cases[m]['max_E_residual_pre'];neg=cases[m]['max_negative_mass']
 a.scatter(i,e,s=80,c=col,zorder=4);a.annotate(f'{e:.2e}',(i,e),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9)
 b.scatter(i,neg,s=80,c=col,zorder=4);b.annotate('0'if neg==0 else f'{neg:.2e}',(i,neg),xytext=(0,10),textcoords='offset points',ha='center',fontsize=9)
a.set_yscale('log');a.set_ylim(5e-17,7e-2);a.set_yticks([1e-16,1e-12,1e-8,1e-4]);a.set_ylabel('Max |U + Eout + W − Uinitial| / Uinitial');a.set_title('Physical-energy ledger defect',fontweight='bold',pad=15)
b.set_ylim(-.000025,.00033);b.set_ylabel('Max integrated negative photon mass / Ninitial');b.ticklabel_format(axis='y',style='sci',scilimits=(0,0));b.set_title('Nonnegative spectrum',fontweight='bold',pad=15)
for ax in [a,b]:
 ax.set_xticks(range(5),labels);ax.set_xlim(-.5,4.5);ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
fig.suptitle('Energy conservation and positivity are separate tests',x=.078,y=.97,ha='left',fontsize=17,fontweight='bold')
fig.text(.078,.865,'Collisionless FLRW diagnostic only · 256 log-spaced cells/panels · PDE CFL coefficient 0.075',fontsize=10.5,color='#444444')
fig.text(.078,.11,'Each dot is a maximum over the 9 saved epochs: s = 0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0.',fontsize=9.5)
fig.text(.078,.064,'Ledger uses each method’s own projected initial energy. Partial-P0 initial energy bias is 5.06e−6; see report for continuum errors.',fontsize=9.1)
fig.text(.078,.022,'No interpolated history. Limited-DG energy includes initial + time-stage limiter changes; its ledger was not repaired.',fontsize=9.1)
fig.savefig(R/'transport_diagnostics.svg',dpi=180);fig.savefig(R/'transport_diagnostics.svg');plt.close(fig)
print('Saved transport_diagnostics.svg and.svg from SUMMARY.json; no new solver epochs.')
