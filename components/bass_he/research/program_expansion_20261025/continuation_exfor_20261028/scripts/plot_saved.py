"""Saved JSON only: no scientific imports, calculation, fitting, or geometry."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def number(x):return float(Fraction(x))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--saved-json',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    saved=Path(a.saved_json);data=json.loads(saved.read_text());out=Path(a.output)
    fig,axes=plt.subplots(2,3,figsize=(13.5,8.5),gridspec_kw={'height_ratios':[1,1.35]})
    colors={4:'#2864a0',8:'#ad4e20'}
    for col,e in enumerate((213,258,330)):
        ax=axes[0,col];rows=[r for r in data['dcs'] if number(r[0])==e]
        ax.errorbar([number(r[1]) for r in rows],[number(r[2]) for r in rows],yerr=[number(r[3]) for r in rows],fmt='o',color='#30383f',capsize=4)
        ax.set(title=f'{e} MeV: literal EXFOR DCS',xlabel='Nominal CM angle (degrees)',ylabel='DCS (nb/sr)');ax.grid(alpha=.18);ax.set_ylim(bottom=0)
        ax=axes[1,col];labels=[];positions=[];tick=0
        for case in (c for c in data['cases'] if c['energy']==e):
            n=case['degree'];endpoint=case['endpoint_zero']
            for name in ('HEMISPHERES','CAPS'):
                obj=case['objectives'][name];r=obj['outer'];label=f"n={n}, {'zero' if endpoint else 'free'}: {name.title()}";labels.append(label);positions.append(tick)
                if r['status']=='EMPTY':ax.text(.04,tick,'empty outer family',color=colors[n],va='center',fontsize=8)
                else:
                    lo,hi=number(r['lower']),number(r['upper']);ax.plot([lo,hi],[tick,tick],color=colors[n],lw=5,solid_capstyle='butt')
                    inner=obj['inner']
                    if inner['status']!='EMPTY':ax.plot([number(inner['lower']),number(inner['upper'])],[tick,tick],color='black',lw=1.5)
                tick+=1
        ax.set_yticks(positions,labels,fontsize=8);ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Same-event coincidence acceptance');ax.grid(axis='x',alpha=.2)
    fig.suptitle('EXFOR11 finite even Bernstein families: data sensitivity and aperture bounds',fontsize=14)
    fig.text(.5,.025,'ERR-S bands are declared sensitivity windows. Colored: outer family enclosure; black: inner family enclosure.\nEndpoint zero is an extrapolation assumption. Uniform azimuth declared. FULL = 1 for each nonempty family.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.075,1,.95));fig.savefig(out/'EXFOR11.png',dpi=160);fig.savefig(out/'EXFOR11.svg');plt.close(fig)
    (out/'PLOT_RECEIPT.json').write_text(json.dumps({'input_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'scientific_imports':0,'science_calls':0,'files':['EXFOR11.png','EXFOR11.svg']},indent=2)+'\n')
