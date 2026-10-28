"""Supplemental all17 log-elapsed-time figure from existing raw pilot cases.

No IVP, rate evaluation, data replacement, or new time samples.
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

UNIT=Path(__file__).resolve().parents[1]
OUT=UNIT/'outputs'
LABELS=('n','H1_0','H1_1','D_0','D_1','T_0','T_1','He3_0','He3_1','He3_2','He4_0','He4_1','He4_2','Li7_0','Li7_1','Li7_2','Li7_3')
FAMILIES=(('n',[0]),('H1',[1,2]),('D',[3,4]),('T',[5,6]),('He3',[7,8,9]),('He4',[10,11,12]),('Li7',[13,14,15,16]))


def main():
    cases={}
    for name in ('OFF_base','ON_base','ON_refined'):
        with np.load(OUT/(name+'.npz'),allow_pickle=False) as d:
            cases[name]={'t':d['t'].copy(),'physical':d['physical'].copy()}
    t=cases['ON_refined']['t']
    if t.ndim!=1 or not np.isfinite(t).all() or np.any(np.diff(t)<=0) or t[0]!=0:
        raise ValueError('invalid saved pilot time schema')
    if any(not np.array_equal(d['t'],t) or d['physical'].shape!=(23,len(t))
           or not np.isfinite(d['physical']).all() for d in cases.values()):
        raise ValueError('saved cases lack the common finite23xN schema')
    positive=t>0
    if not positive.any():raise ValueError('no positive elapsed-time samples')
    fig,axes=plt.subplots(7,1,figsize=(10,17),sharex=True)
    for ax,(family,indices) in zip(axes,FAMILIES):
        has_positive=False;has_negative=False
        for j,index in enumerate(indices):
            color=plt.get_cmap('tab10')(j)
            label='n' if index==0 else family+' '+('I','II','III','IV')[j]
            for name,style,lw in (('OFF_base','--',1.),('ON_base',':',1.),('ON_refined','-',1.7)):
                values=cases[name]['physical'][index,positive]
                has_positive=has_positive or bool(np.any(values>0))
                has_negative=has_negative or bool(np.any(values<0))
                ax.plot(t[positive],np.ma.masked_less_equal(values,0),style,color=color,lw=lw,
                        label=label if name=='ON_refined' else None)
        ax.set_xscale('log')
        if has_positive:ax.set_yscale('log')
        else:ax.set_ylim(0,1);ax.text(.5,.5,'No positive log-domain samples',ha='center',transform=ax.transAxes)
        if family in ('n','T') and np.all(cases['OFF_base']['physical'][indices]==0):
            ax.text(.99,.07,'OFF '+family+' = exact zero (raw data retained)',ha='right',fontsize=8,transform=ax.transAxes)
        if has_negative:
            ax.text(.99,.17,'Signed samples retained in CSV; omitted on log axis',ha='right',fontsize=7,transform=ax.transAxes)
        ax.set_ylabel(family+'\nparticles / Href');ax.grid(alpha=.2,which='both');ax.legend(fontsize=8,ncol=4)
    axes[-1].set(xlim=(float(t[positive].min()),float(t.max())),xlabel='Elapsed proper time after source turn-on [s]')
    handles=[Line2D([0],[0],color='black',ls=style,label=label) for label,style in
             (('OFF base','--'),('ON base',':'),('ON refined','-'))]
    fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.5,.975),ncol=3,fontsize=9)
    fig.suptitle('All17 populations versus elapsed proper time — illustrative prescribed-bath pilot',y=.995)
    fig.text(.5,.012,'t = 0 is omitted from the logarithmic axis; all361 raw samples remain unchanged. No epsilon floors.\nLi7 IV included; abundances are particles / Href. Hidden Li6 remains prescribed. Existing three cases only.',ha='center',fontsize=9)
    fig.tight_layout(rect=(0,.045,1,.955));fig.savefig(OUT/'pilot17_logtime.png',dpi=150);plt.close(fig)
    (OUT/'PILOT_LOGTIME_FIGURE.json').write_text(json.dumps({'status':'COMPLETED_FROM_EXISTING_CASES',
        'output':'pilot17_logtime.png','raw_samples_per_case':len(t),'plotted_positive_times':int(positive.sum()),
        'omitted_t0':True,'abundance_floor_added':False,'negative_samples_masked_only_for_plot':True,
        'included_states':list(LABELS),'IVP_execution':'NONE','new_numeric_samples':'NONE'},indent=2)+'\n')


if __name__=='__main__':main()
