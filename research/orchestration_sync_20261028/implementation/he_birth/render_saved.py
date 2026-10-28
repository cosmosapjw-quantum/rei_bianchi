"""Plot saved per-sample moment intervals and exact pair anticorrelation."""
import pathlib,json
from fractions import Fraction as F
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path(__file__).resolve().parent
d=json.loads((ROOT/'results.json').read_text());rows=d['rows'];K=float(F(d['constants']['K0_MeV']));plt.rcParams.update({'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False});fig,axes=plt.subplots(1,2,figsize=(13,5.8))
colors={'FULL':'#1f648b','HEMISPHERES':'#d18130','CAPS':'#32806a'}
for aperture in ['FULL','HEMISPHERES','CAPS']:
    points=[r for r in rows if r['aperture']==aperture]
    for i,r in enumerate(points):
        lo,hi=[float(F(v)) for v in r['daughter_variance_MeV2']];offset={'FULL':-.18,'HEMISPHERES':0,'CAPS':.18}[aperture];axes[0].plot([i+offset]*2,[lo,hi],color=colors[aperture],lw=4);axes[0].scatter([i+offset],[(lo+hi)/2],color=colors[aperture],s=30,label=aperture if i==0 else None)
samples=list(dict.fromkeys(r['sample'] for r in rows));axes[0].set(xticks=range(len(samples)),xticklabels=['Witness']+['N16 v'+str(i) for i in range(len(samples)-1)],ylabel='Variance of either daughter [MeV²]',title='Exact interval bounds for 5 frozen samples');axes[0].legend();axes[0].grid(axis='y',alpha=.2)
# Plot covariance matrix from a saved FULL fixed-witness exact moment.
fixed=next(r for r in rows if r['sample']=='fixed_witness' and r['aperture']=='FULL');v=float(F(fixed['daughter_variance_MeV2'][0]));matrix=[[v,-v],[-v,v]];image=axes[1].imshow(matrix,cmap='RdBu',vmin=-v,vmax=v)
for i in range(2):
    for j in range(2):axes[1].text(j,i,f'{matrix[i][j]:.4f}',ha='center',va='center',color='white',fontsize=12)
axes[1].set(xticks=[0,1],yticks=[0,1],xticklabels=['K+','K−'],yticklabels=['K+','K−'],title='Fixed witness, FULL: covariance [MeV²]');fig.colorbar(image,ax=axes[1],shrink=.75)
fig.suptitle('Conditional two-deuteron birth moments • exact daughter anticorrelation',fontsize=14);fig.text(.5,.045,f'Mean(K±) = {K:.8f} MeV (approx.); pair total = {2*K:.8f} MeV (approx.), pair-total variance = 0 exactly.',ha='center',fontsize=10);fig.text(.5,.01,'Intervals use saved aperture threshold enclosures. Per-sample conditional reference only; birth pool UNASSIGNED, deposition null.',ha='center',fontsize=9);fig.tight_layout(rect=(0,.09,1,.94));fig.savefig(ROOT/'DIAGNOSTIC.svg');fig.savefig(ROOT/'DIAGNOSTIC.png',dpi=130)
