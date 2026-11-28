"""One render: manufactured phase algebra and actual printed TP ratios."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]


def main():
    data=json.loads((UNIT/'results/source_analysis.json').read_text())
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'figure.dpi':130})
    fig,(left,right)=plt.subplots(1,2,figsize=(10.4,4.7))
    phases=data['manufactured_phase_controls']
    xs=[p['phase_rad'] for p in phases]
    for spin,color,label in [(0,'#2563a6','Singlet S=0'),(1,'#a54822','Triplet S=1')]:
        left.plot(xs,[p['channels'][str(spin)]['C']['float'] for p in phases],color=color,label=label,lw=2)
    left.axhspan(0,4,color='#687b84',alpha=.10,label='Free-phase range [0,4]')
    left.set(xlabel='Relative phase (radians)',ylabel='Coherent density (arbitrary units)',
             title='Manufactured controls: a=1, b=exp(i phase)',xlim=(0,3.141592653589793),ylim=(-.1,4.35))
    left.set_xticks([0,1.5707963267948966,3.141592653589793],['0','pi/2','pi'])
    left.legend(loc='center',frameon=False,fontsize=8.5)
    for energy,color,marker in [('2','#2563a6','o'),('3','#a54822','s')]:
        rows=[r for r in data['comparisons'] if r['total_three_body_energy_Ryd']==energy]
        right.plot([int(r['N']) for r in rows],[float(r['published_over_BRM']) for r in rows],
                   color=color,marker=marker,lw=1.5,label=f'Total energy {energy} Ry')
    right.axhline(1,color='#414a50',ls='--',lw=1,label='Printed BRM reference')
    right.set(xlabel='Basis size N (source order preserved)',ylabel='Published 4CCC / printed BRM',
              title='Real source: Stelbovics Table I, TP singlet')
    right.legend(loc='upper right',frameon=False,fontsize=8.5)
    for ax in (left,right):
        ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Equal-sharing convention checks: phase and normalization',fontsize=13,y=.97)
    fig.text(.5,.045,'Table I already includes factor four; no new normalization. TP energy DCS is not a full H angular payload.',
             ha='center',fontsize=9)
    fig.subplots_adjust(left=.075,right=.98,bottom=.19,top=.84,wspace=.28)
    fig.savefig(UNIT/'figures/ccc_exchange_source_controls.png')
    fig.savefig(UNIT/'figures/ccc_exchange_source_controls.svg')
    plt.close(fig)
    print('Saved manufactured-phase / real-TP-table figure pair.')


if __name__=='__main__':main()
