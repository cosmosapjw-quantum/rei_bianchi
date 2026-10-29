"""Two source-conditional graphics; connecting knots are interpolant guides, not a physical IVP."""
from pathlib import Path
import sys,csv, collections
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'

def run():
    cum=list(csv.DictReader((R/'CUMULATIVE_14_KNOT_EXPOSURE.csv').open()))
    events=list(csv.DictReader((R/'INTERVAL_84_EVENT_EXPOSURE.csv').open()))
    fig,ax=plt.subplots(figsize=(9.4,5.5),layout='constrained')
    for label,style in [('P19_D1_fiducial','-o'),('P19_D1_BB13_GLs_nominal','--s')]:
        x=sorted([r for r in cum if r['scenario']==label],key=lambda r:float(r['elapsed_proper_s']))
        ax.plot([float(r['elapsed_proper_s'])/1e16 for r in x],
            [float(r['loglinear_photoelectrons_per_Href']) for r in x],style,label=label)
    ax.set_xlabel('Original frozen REI elapsed proper time (10$^{16}$ s)')
    ax.set_ylabel('Cumulative conditional photoionizations per Href')
    ax.set_title('Conditional exposure from seven frozen knots\nNot a P19 chemical evolution or optical depth')
    ax.grid(alpha=.22);ax.legend(fontsize=8)
    fig.savefig(R/'CUMULATIVE_EXPOSURE.png',dpi=160)
    plt.close(fig)
    groups={'H1':[1],'D':[2],'T':[3],'He3':[4,5],'He4':[6,7]}
    fig,ax=plt.subplots(figsize=(9.4,5.4),layout='constrained')
    xs=list(groups); y0=[];y1=[]
    for k, v in groups.items():
        vals=[]
        for label in ['P19_D1_fiducial','P19_D1_BB13_GLs_nominal']:
            vals.append(sum(float(r['loglinear_photoelectrons_per_Href']) for r in events if r['scenario']==label and int(r['event_index']) in v))
        y0.append(vals[0]);y1.append(vals[1])
    import numpy as np
    positions=np.arange(len(xs));bw=.37
    ax.bar(positions-bw/2,y0,width=bw,label='P19 fiducial')
    ax.bar(positions+bw/2,y1,width=bw,label='P19 + BB13 nominal')
    ax.set_xticks(positions,xs)
    ax.set_ylabel('Integrated conditional photoionizations per Href')
    ax.set_title('Seven REI photo-event contributions, grouped by isotope\nConditional time interpolation, not a physical history')
    ax.set_yscale('log')
    ax.grid(axis='y',alpha=.2)
    ax.legend(fontsize=8)
    fig.savefig(R/'ISOTOPE_EXPOSURE_COMPONENTS.png',dpi=160)
    plt.close(fig)
    return [str(R/'CUMULATIVE_EXPOSURE.png'),str(R/'ISOTOPE_EXPOSURE_COMPONENTS.png')]
if __name__=='__main__':print(run())
