"""Presentation-only saved data rendering. Scientific module imports/calls: zero."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    p=argparse.ArgumentParser();p.add_argument('--saved',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=True,parents=True)
    saved=json.loads(a.saved.read_text());number=lambda v:float(Fraction(v))
    fig,(left,right)=plt.subplots(1,2,figsize=(13,5.2),layout='constrained')
    curve=saved['plot']['curve_samples'];left.plot([number(s['mu']) for s in curve],[number(s['dcs']) for s in curve],color='#2456a6',label='Fixed rational sextic witness')
    for row in saved['plot']['data_windows']:
        lo,hi=map(number,row['window']);ml,mh=map(number,row['mu_interval']);left.errorbar([(ml+mh)/2],[(lo+hi)/2],yerr=[(hi-lo)/2],fmt='o',color='#b05225',capsize=5)
    left.set(xlabel=r'$\mu=\cos\theta_{cm}$',ylabel='DCS (nb/sr)',title='330 MeV: endpoint-zero sextic witness',xlim=(-1.03,1.03));left.grid(alpha=.2);left.legend(fontsize=8)
    colors={'HEMISPHERES':'#2456a6','CAPS':'#a54824'}
    for geometry,offset in [('HEMISPHERES',.12),('CAPS',-.12)]:
        for i,case in enumerate(saved['cases']):
            obj=case['objectives'][geometry];lo,hi=map(number,obj['physical_range']);minlo,minhi=map(number,obj['minimum_bracket']);maxlo,maxhi=map(number,obj['maximum_bracket']);y=i+offset
            right.plot([lo,hi],[y,y],color=colors[geometry],alpha=.3,lw=7)
            right.plot([minlo,minhi],[y,y],color=colors[geometry],lw=2,marker='|',markersize=9)
            right.plot([maxlo,maxhi],[y,y],color=colors[geometry],lw=2,marker='|',markersize=9,label=geometry if i==0 else None)
    right.set(yticks=[0,1,2],yticklabels=['N=1','N=4','N=16'],xlabel='Same-event probability',title='Outer range and feasible extremum brackets',xlim=(0,1));right.grid(axis='x',alpha=.2);right.legend(fontsize=8)
    fig.suptitle('ENDPOINT14 • conditional model and deterministic EXFOR sensitivity windows',fontsize=12)
    png=a.output/'ENDPOINT14_REFERENCE.png';svg=a.output/'ENDPOINT14_REFERENCE.svg';fig.savefig(png,dpi=140);fig.savefig(svg);plt.close(fig)
    receipt={'status':'PASS','scientific_imports':0,'scientific_calls':0,'saved_input_sha256':hashlib.sha256(a.saved.read_bytes()).hexdigest(),'outputs':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size':p.stat().st_size} for p in (png,svg)},'ordinary_scale_axes':True,'render_count':1}
    (a.output/'PLOT_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt));return 0
if __name__=='__main__':sys.exit(main())
