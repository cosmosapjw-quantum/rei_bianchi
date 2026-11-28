"""QUARTIC12 saved-JSON-only figure; no scientific module imports or recomputation."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def num(x):return float(Fraction(x))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--saved-json',required=True);p.add_argument('--output',required=True);a=p.parse_args();saved=Path(a.saved_json);data=json.loads(saved.read_text());out=Path(a.output)
    fig,axes=plt.subplots(2,3,figsize=(14.5,8.8),gridspec_kw={'height_ratios':[1,1.4]})
    colors={'free_N1':'#2864a0','free_N4':'#bd611d','free_N16':'#308056','endpointzero_exact':'#8552a0'}
    for col,e in enumerate((213,258,330)):
        ax=axes[0,col];rows=[r for r in data['dcs'] if num(r[0])==e]
        ax.errorbar([num(r[1]) for r in rows],[num(r[2]) for r in rows],yerr=[num(r[3]) for r in rows],fmt='o',capsize=4,color='#28333d');ax.set(title=f'{e} MeV: literal EXFOR DCS',xlabel='Nominal CM angle (degrees)',ylabel='DCS (nb/sr)');ax.set_ylim(bottom=0);ax.grid(alpha=.2)
        ax=axes[1,col];positions=[];labels=[];tick=0
        for case in (c for c in data['cases'] if c['energy']==e):
            name=case['case'];label=('Endpoint zero exact' if case['endpoint_zero'] else f"Free N={case['N']}")
            for detector in ('HEMISPHERES','CAPS'):
                obj=case['objectives'][detector];positions.append(tick);labels.append(label+': '+detector.title());color=colors[name]
                if obj['physical_range'] is None:ax.text(.025,tick,'empty physical intersection' if obj['status']=='EMPTY_PHYSICAL_INTERSECTION' else 'empty outer',va='center',fontsize=8,color=color)
                else:
                    lo,hi=map(num,obj['physical_range']);ax.plot([lo,hi],[tick,tick],lw=5,color=color,solid_capstyle='butt',alpha=.85)
                    minimum=obj['minimum_bracket'];maximum=obj['maximum_bracket']
                    for point in (minimum[1],maximum[0]):
                        if point is not None:ax.plot([num(point)],[tick],marker='|',color='black',markersize=10,markeredgewidth=1.4)
                    if case['inner_witness'] is None:ax.text(.98,tick,'no inner',ha='right',va='center',fontsize=7,color='#444')
                tick+=1
        ax.set_yticks(positions,labels,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Same-event coincidence acceptance');ax.grid(axis='x',alpha=.2)
    fig.suptitle('QUARTIC12: full nonnegative even quartic family, finite positivity sandwiches',fontsize=14)
    fig.text(.5,.025,'Colored segments: certified outer physical enclosure. Black ticks: inner attained-witness bounds on minimum and maximum.\nERR-S windows are sensitivity choices; uniform azimuth declared. N fixes positivity mesh; endpoint zero is a separate exact family. FULL = 1 when nonempty.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.075,1,.95));fig.savefig(out/'QUARTIC12.png',dpi=160);fig.savefig(out/'QUARTIC12.svg');plt.close(fig)
    (out/'PLOT_RECEIPT.json').write_text(json.dumps({'input_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'scientific_imports':0,'science_calls':0,'files':['QUARTIC12.png','QUARTIC12.svg']},indent=2)+'\n')
