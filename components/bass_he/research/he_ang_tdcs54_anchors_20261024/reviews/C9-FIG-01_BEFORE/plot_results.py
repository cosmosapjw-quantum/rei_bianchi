"""Sparse source points and exact nominal minimax diagnostics; one render."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

UNIT=Path(__file__).resolve().parents[1]


def number(q):return float(q['decimal'])


def main():
    result=json.loads((UNIT/'results/source_analysis.json').read_text())
    rows=result['source_rows_literal'];located=[rows[i] for i in [1,3]]
    plt.rcParams.update({'font.size':10,'axes.titlesize':11,'figure.dpi':130})
    fig,(left,right)=plt.subplots(1,2,figsize=(11.2,5.3))
    for column,label,color,marker in [('CDW_EIS_TDCS_au','CDW-EIS','#2563a6','^'),
        ('CCC99_TDCS_au','CCC99','#b34c20','s'),('experiment_TDCS_au','Experiment','#20262b','D')]:
        left.scatter([float(r['fast_angle_counterclockwise_deg']) for r in located],
                     [float(r[column]) for r in located],label=label,c=color,marker=marker,s=62,zorder=3)
    left.set(xlabel='Fast electron angle CCW (degrees)',ylabel='Reported TDCS (source atomic units)',
             title='Two located H(1s) joint TDCS points',xlim=(2,12),ylim=(0,2.9))
    left.set_xticks([4,10]);left.legend(frameon=False,loc='lower left')
    left.text(.03,.95,'Incident 54.4 eV; slow 5 eV\nSlow angle 210 degrees CW',transform=left.transAxes,va='top',fontsize=9)
    names=['located_anchors_2','binary_peak_heights_4','all_reported_features_8']
    for j,(label,color) in enumerate([('CDW_EIS','#2563a6'),('CCC99','#b34c20')]):
        xs=[i+(j-.5)*.31 for i in range(3)]
        ys=[100*number(result['groups'][n]['models'][label]['optimum']['free_delta']) for n in names]
        right.bar(xs,ys,width=.28,label=label.replace('_','-'),color=color,alpha=.85)
        for x,y in zip(xs,ys):right.text(x,y+.5,f'{y:.2f}%',ha='center',fontsize=8)
        for i in [1,2]:
            summary=result['groups'][names[i]]['models'][label]['paper_approximate_summary']
            right.scatter(xs[i],float(summary['reported_percent'].rstrip('%')),marker='D',s=42,
                          facecolors='white',edgecolors='#20262b',zorder=4,
                          label='Paper approximate summary' if j==0 and i==1 else None)
    right.axhline(10,color='#4b5660',ls='--',lw=1,label='Nominated delta=10% scenario')
    right.set_xticks([0,1,2],['2 located\nanchors','4 binary\npeak heights','All 8 reported\nfeatures'])
    right.set(ylabel='Free-scale minimum relative half-width (%)',title='Exact nominal minimax shape diagnostics',ylim=(0,38))
    right.legend(loc='upper left',frameon=False,fontsize=8)
    for ax in (left,right):ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Jones & Madison (2000), Table IV: sparse TDCS and common-scale comparison',fontsize=13,y=.97)
    fig.text(.5,.06,'Points are not interpolated. Peak heights with unknown slow angles are features, not additional located points.',ha='center',fontsize=9)
    fig.text(.5,.025,'Paper summaries are descriptive; delta=10% is a nominated deterministic scenario, not a confidence interval.',ha='center',fontsize=9)
    fig.subplots_adjust(left=.075,right=.98,bottom=.2,top=.84,wspace=.27)
    fig.savefig(UNIT/'figures/tdcs54_source_controls.png');fig.savefig(UNIT/'figures/tdcs54_source_controls.svg');plt.close(fig)
    print('Saved two-panel source/diagnostic PNG and SVG; no interpolation or new solver.')


if __name__=='__main__':main()
