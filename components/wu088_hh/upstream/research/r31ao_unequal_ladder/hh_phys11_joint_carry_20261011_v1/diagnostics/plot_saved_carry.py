"""Render already saved enclosure endpoints; no scientific model execution."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'results/carry_v2/CARRY_RESULTS.json').read_text())
fig,axes=plt.subplots(1,2,figsize=(11,5.5),sharey=True)
for ax,stage in zip(axes,data['stages'],strict=True):
    for g in stage['groups']:
        if not 16<=g['node']<=24:continue
        x=g['node'];lo=g['outgoing_joint']['W']['lo'];hi=g['outgoing_joint']['W']['hi']
        color='#155e75' if lo>0 else '#b45309'
        ax.vlines(x,lo,hi,color=color,linewidth=3)
        ax.hlines([lo,hi],x-.18,x+.18,color=color,linewidth=1.5)
    ax.set_yscale('symlog',linthresh=1e-26,linscale=.5)
    ax.set_yticks([-1e-20,-1e-23,0,1e-23,1e-20,1e-17])
    ax.axhline(0,color='#94a3b8',linewidth=.7)
    ax.set_xlim(15.5,24.5);ax.set_xticks(range(16,25))
    ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    ax.set_title('Full: d = 1.25e9 s' if stage['stage']=='full' else 'First half: d = 6.25e8 s')
    ax.set_xlabel('Energy node index (zero-based)')
    ax.spines[['top','right']].set_visible(False)
axes[0].set_ylabel('Mixed photon response W_N  [photons / H]')
fig.suptitle('PHYS11: spectral carry has both signs',fontsize=16,y=.98)
fig.text(.5,.035,'Bars are uniform enclosures, not statistical error bars. Both steps start from the same COMMON.\nNode24: 13.7eV birth; nodes16-23: 13.6-13.6875eV. Other24 nodes contain zero and are omitted.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.11,1,.92))
out=ROOT/'figures';out.mkdir(exist_ok=True)
fig.savefig(out/'SPECTRAL_MIXED_CARRY.png',dpi=180)
fig.savefig(out/'SPECTRAL_MIXED_CARRY.pdf',metadata={'Title':'PHYS11 spectral mixed carry','Author':'WU088_HH research loop'})
print('Rendered saved endpoints to2figures; source/root/inverse calls0.')
