#!/usr/bin/env python3
"""Render the actual selected-path width ratios, with no physics invocation."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1]);a=ap.parse_args();root=a.package.resolve()
    source=root/'analysis/ACTUAL_PORTABLE/LOCAL_ANALYSIS.json';d=json.loads(source.read_bytes());out=root/'figures';out.mkdir(exist_ok=True)
    paths=d['paths'];labels=['1\nHI','1162\nHI + HeI','1976\nAll species','1620\nMask event','2344\nSource event'];x=np.arange(len(paths))
    fig,axs=plt.subplots(1,2,figsize=(12.4,6.2),sharey=True)
    for ax,q,title in zip(axs,['P_final','H_total_eV'],['Photon stock P','Heat H']):
        def values(level):
            return [float(F(next(z['candidate_width'] for z in p['levels'][level]['comparison_rows'] if z['kind']=='absolute' and z['quantity']==q))/F(next(z['baseline_width'] for z in p['levels'][level]['comparison_rows'] if z['kind']=='absolute' and z['quantity']==q))) for p in paths]
        low,high,final=values('M32'),values('M128'),values('SELECTED')
        ax.bar(x-.18,low,.34,label='M32 diagnostic',color='#abb9c5',edgecolor='white')
        ax.bar(x+.18,high,.34,label='M128',color='#266d95',edgecolor='white')
        ax.scatter([x[1]+.18],[final[1]],s=95,marker='D',color='#dc7734',edgecolor='white',linewidth=.8,zorder=4,label='M256: node 1162 only')
        ax.axhline(1,color='#444444',lw=1,ls='--');ax.text(4.48,1.012,'Baseline',ha='right',fontsize=9,color='#444444')
        ax.set_xticks(x,labels,fontsize=10);ax.set_title(title,fontsize=14,pad=12)
        ax.set_ylim(0,1.09);ax.set_yticks([0,.25,.5,.75,1],['0%','25%','50%','75%','100%'])
        ax.grid(axis='y',alpha=.17);ax.set_axisbelow(True)
        for sp in ['top','right']:ax.spines[sp].set_visible(False)
        for j,v in enumerate(final):ax.text(x[j]+.18,v+.023,f'{100*(1-v):.1f}% less',ha='center',fontsize=8.2,color='#173548')
    axs[0].set_ylabel('Raw enclosure width / same-path admitted baseline',fontsize=11)
    handles,legends=axs[0].get_legend_handles_labels();fig.legend(handles,legends,loc='lower center',bbox_to_anchor=(.5,.185),ncol=3,frameon=False,fontsize=10)
    fig.suptitle('Signed second-Volterra correction: five captured OFF paths',fontsize=17,y=.97)
    fig.text(.5,.105,'Selected weighted sums: P width −32.57%  |  H width −30.48%  |  170 / 170 raw intervals nested',ha='center',fontsize=11,weight='bold',color='#173548')
    fig.text(.5,.025,'First-variation quadrature reused at N512/N1024, P60. M controls only the new signed correction.\nFinite selected paths only; these percentages are not full-population or physical-error estimates.',ha='center',fontsize=9,color='#505a61')
    fig.subplots_adjust(left=.075,right=.985,top=.83,bottom=.32,wspace=.15)
    name='E13C9_SELECTED_WIDTHS'
    fig.savefig(out/(name+'.png'),dpi=180,facecolor='white')
    fig.savefig(out/(name+'.svg'),facecolor='white')
    plt.close(fig)
    pins={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [source,Path(__file__),out/(name+'.png'),out/(name+'.svg')]}
    (out/'FIGURE_PROVENANCE.json').write_text(json.dumps({'source':str(source.relative_to(root)),'pins':pins,'matplotlib_version':matplotlib.__version__,'scientific_kernel_calls':0},indent=2)+'\n')
    print(json.dumps({'figure':str(out/(name+'.png')),'pins':pins},indent=2))


if __name__=='__main__':main()
