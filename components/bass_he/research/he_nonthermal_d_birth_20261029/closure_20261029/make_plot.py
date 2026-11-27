"""New source-only figure; reuse saved validation data, never old campaigns."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,math
import numpy as np
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from energy_gain import SexticLaw,FULL_WITNESS
from nonthermal_d_birth import K0_MEV
from conditional_pressure_trace import B2_MEV2
law=SexticLaw(FULL_WITNESS)
d=json.loads((ROOT/'evidence/NUMERICAL_REFERENCE.json').read_text())
rows=d['intervals'];b=math.sqrt(float(B2_MEV2));k0=float(K0_MEV)
x=np.linspace(-1,1,501);a0,a1,a2=map(float,law.coefficients)
y=2*(1-x*x)*(a0+a1*x*x+a2*x**4)/float(law.normalization)/b
fig,axes=plt.subplots(1,3,figsize=(13.2,4.2),layout='constrained')
axes[0].plot(k0+b*x,y,color='#246a93',lw=2)
axes[0].set(xlabel='D kinetic energy K [MeV]',ylabel='D / (event MeV)',title='Chosen sextic energy gain')
axes[0].axvline(k0,color='0.55',lw=.8,ls=':')
err=float(d['midpoint_mutant_kinetic_error_MeV'])
axes[1].bar(['Integrated first moment','Bin midpoint mutant'],[0,err],color=['#287a60','#b94739'])
axes[1].axhline(0,color='0.3',lw=.8)
axes[1].set(ylabel='Pair kinetic residual [MeV/event]',title='Same asymmetric 4-bin partition')
axes[1].tick_params(axis='x',labelsize=8)
axes[1].text(1,err*1.01,f'+{err:.6f}',ha='center',va='bottom',fontsize=9)
axes[1].set_ylim(-.06,err*1.22)
widths=[float(F(r['width_exact'])) for r in rows]
axes[2].semilogy(range(7),widths,'o-',color='#246a93',label='Full-law intersection')
axes[2].axhline(widths[0],color='0.5',ls='--',label='m2-only universal')
axes[2].set(xlabel='Series order N',ylabel='Trace enclosure width [MeV/event]',title='Exact rational remainder')
axes[2].legend(fontsize=8)
for ax in axes:ax.grid(alpha=.2,axis='y')
fig.suptitle('Conditional He4 + gamma(330 MeV) -> 2D: source-only diagnostic',fontsize=13)
fig.supxlabel('Frozen target-rest masses; selected normalized angular law; physical rate / stopping unresolved',fontsize=9)
out=ROOT/'results';out.mkdir(exist_ok=True)
fig.savefig(out/'conditional_gain_trace.png',dpi=160)
fig.savefig(out/'conditional_gain_trace.svg')
(out/'PLOT_DATA.json').write_text(json.dumps({'source_reference':'../evidence/NUMERICAL_REFERENCE.json','x':x.tolist(),'K_MeV':(k0+b*x).tolist(),'inclusive_density_per_event_MeV':y.tolist(),'widths_exact':[r['width_exact'] for r in rows],'midpoint_error_MeV':d['midpoint_mutant_kinetic_error_MeV'],'scope':'conditional frozen law; no physical event rate'},indent=2)+'\n')
print(str(out/'conditional_gain_trace.png'))
