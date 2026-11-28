"""Render only the new ANGULAR06 stored outputs; import no physics module."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'evidence/validation/SAVED_PLOT_DATA.json').read_text())
out=ROOT/'evidence/plot';out.mkdir(parents=True,exist_ok=True)
fig,axes=plt.subplots(1,3,figsize=(13.6,4.25),layout='constrained')
colors=['#176c9c','#bd5b26','#277d66']
for curve,color in zip(data['synthetic_curves'],colors):
    pts=[r for r in curve['values'] if r['nu'] is not None]
    axes[0].plot([r['mu'] for r in pts],[r['nu'] for r in pts],color=color,lw=2,label=f"a={curve['a']}")
    folds=[r for r in pts if r['status']=='FOLD']
    for r in folds:axes[0].scatter([r['mu']],[r['nu']],s=35,color=color,zorder=5)
axes[0].set(xlabel='CM cosine μ',ylabel='Lab cosine ν',title='A  Angular map (synthetic γ=1.25)',xlim=(-1,1),ylim=(-1.05,1.05))
axes[0].legend(frameon=False);axes[0].grid(alpha=.18)
for energy,color in zip([213,258,330],colors):
    pts=[r for r in data['native'] if float(r['source_values']['EN'])==energy]
    for side,style in [('plus','-'),('minus','--')]:
        axes[1].plot([float(r['source_values']['ANG-CM']) for r in pts],
                     [abs(r[side]['jacobian_signed']) for r in pts],style,marker='o',color=color,
                     label=f'{energy} MeV, {side}')
axes[1].set(xlabel='Native CM angle (degrees)',ylabel='|dν/dμ|',title='B  Native-coordinate Jacobians')
axes[1].legend(frameon=False,fontsize=7.4,ncol=2);axes[1].grid(alpha=.18)
pts=data['synthetic_fold_density']
axes[2].loglog([r['delta_nu'] for r in pts],[r['density'] for r in pts],color=colors[2],lw=2)
axes[2].set(xlabel='ν − νmin',ylabel='Pushforward density per dν',title='C  Fold density (synthetic f=1/2)')
axes[2].grid(which='both',alpha=.18)
fig.suptitle('ANGULAR06: conditional transport; experimental normalization remains open',fontsize=13)
fig.savefig(out/'ANGULAR06_TRANSPORT.png',dpi=140)
fig.savefig(out/'ANGULAR06_TRANSPORT.svg')
plt.close(fig)
(out/'PLOT_DATA.json').write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
