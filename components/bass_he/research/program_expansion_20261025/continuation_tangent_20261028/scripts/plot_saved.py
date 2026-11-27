"""Render saved display values only. Does not import any scientific producer."""
import argparse
import hashlib
import json
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--saved',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    raw=a.saved.read_bytes();data=json.loads(raw)
    fig,axes=plt.subplots(1,2,figsize=(10,4.2))
    for ax,geom in zip(axes,['HEMISPHERES','CAPS']):
        o=data['objectives'][geom];lo,hi=o['outward_float_bracket']
        ax.plot([lo,hi],[0,0],color='#156b73',linewidth=5,marker='|',markersize=20)
        ax.scatter([(lo+hi)/2],[0],s=22,color='#d66c2d',zorder=3)
        ax.set_xlim(lo-(hi-lo)*.3,hi+(hi-lo)*.3)
        ax.set_ylim(-1,1);ax.set_yticks([]);ax.ticklabel_format(axis='x',style='plain',useOffset=True)
        ax.set_title(geom);ax.set_xlabel('Certified minimum aperture fraction')
        ax.text(.5,.9,'['+o['outward_decimal_endpoints'][0]+',\n'+o['outward_decimal_endpoints'][1]+']',ha='center',va='top',transform=ax.transAxes,fontsize=9)
        ax.text(.5,.1,'Bracket width ≈ '+format(o['display_width_float'],'.3e'),ha='center',transform=ax.transAxes)
        for spine in ['top','right','left']:ax.spines[spine].set_visible(False)
    fig.suptitle('TANGENT13 · 258 MeV full nonnegative quartic minima',fontsize=13)
    fig.text(.5,.015,'Fixed coordinate ERR-S sensitivity windows; computational brackets, not experimental uncertainty.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.05,1,.94))
    outputs=[]
    for ext in ['png','svg']:
        target=a.output/('TANGENT13.'+ext);fig.savefig(target,dpi=160);outputs.append({'path':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    (a.output/'PLOT_RECEIPT.json').write_text(json.dumps({'status':'PASS','input_sha256':hashlib.sha256(raw).hexdigest(),'saved_only':True,'science_calls':0,'outputs':outputs},indent=2)+'\n')

if __name__=='__main__':main()
