"""Saved-result plots only; never integrates or joins different models."""
from pathlib import Path
import json,csv,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coordinates import c15_normalized
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'svg.fonttype':'none','font.size':10})

def save(fig,name):
    fig.tight_layout()
    for ext in ('png','svg','pdf'):fig.savefig(ROOT/'plots'/f'{name}.{ext}',dpi=170)
    plt.close(fig)

def write_csv(path,rows):
    if rows:
        with path.open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def c15():
    p=ROOT/'data/original/C15_STUDY_RESULTS.json';assert hashlib.sha256(p.read_bytes()).hexdigest()=='40c0ae6325fdba5cf47f8240ee655769c1f236351a2c9004e7f3488d16647b7e'
    data=json.loads(p.read_text());out=[];fig,axes=plt.subplots(1,2,figsize=(12,5))
    for series in data['series']:
        name=series['scientific_case'];control=name=='GRAVITY_PI_DISABLED_CONTROL';history=[dict(series=name,saved_index=i,a=r['a'],**c15_normalized(r,control)) for i,r in enumerate(series['history'])];out+=history
        ax=axes[int(control)];line=ax.plot([r['u'] for r in history],[r['v'] for r in history],label=name)[0];ax.scatter(history[0]['u'],history[0]['v'],marker='o',facecolors='none',edgecolors=line.get_color());ax.scatter(history[-1]['u'],history[-1]['v'],marker='x',color=line.get_color())
    for ax,title in zip(axes,['C15: seven physical saved series','C15: gravity-stress-disabled control']):
        ax.set(title=title,xlabel='signed u = sqrt(6) s/H',ylabel='signed physical v');ax.set_xscale('symlog',linthresh=1e-12);ax.set_yscale('symlog',linthresh=1e-15);ax.set_xticks([-1e-2,-1e-6,0,1e-6,1e-2]);ax.grid(alpha=.25);ax.legend(fontsize=7)
    fig.suptitle('C15 original saved rows only: a=0.1999 → 0.2\n○ first saved post-step, × final; control physical stress retained',fontsize=12)
    save(fig,'c15_signed_saved');write_csv(ROOT/'data/results/c15_normalized.csv',out)
    (ROOT/'data/results/c15_normalized.json').write_text(json.dumps(dict(rows=out,series=8,physical_series=7,control_series=1,first_saved='post-step, not initial',model='C13 H/He native narrow interval; distinct from canonical pilot'),indent=2)+'\n')

def pilot():
    results=[json.loads(p.read_text()) for p in sorted((ROOT/'data/results/cases').glob('s*_p*.json'))];good=[r for r in results if r['status']=='completed']
    if not good:return
    fig,axes=plt.subplots(1,3,figsize=(14,4.8));summary=[]
    for r in good:
        h=r['normalized_history'];sgn=r['inputs']['stress_sign'];color={-1:'tab:blue',0:'gray',1:'tab:red'}[sgn]
        axes[0].plot([x['u'] for x in h],[x['v'] for x in h],color=color,alpha=.65,lw=.8);axes[0].scatter(h[0]['u'],h[0]['v'],marker='o',facecolors='none',edgecolors=color,s=12);axes[0].scatter(h[-1]['u'],h[-1]['v'],marker='x',color=color,s=18)
        for ax,key in zip(axes[1:],['Sigma_F','Pi_F']):ax.plot([x['a'] for x in h],[x[key] for x in h],color=color,alpha=.6,lw=.8)
        summary.append(dict(case_id=r['case_id'],status=r['status'],stress_sign=sgn,requested_Sigma_F=r['inputs']['Sigma_F'],requested_Pi_F=r['inputs']['Pi_F'],initial_u=h[0]['u'],initial_v=h[0]['v'],final_u=h[-1]['u'],final_v=h[-1]['v'],initial_Sigma_F=h[0]['Sigma_F'],initial_Pi_F=h[0]['Pi_F'],final_Sigma_F=h[-1]['Sigma_F'],final_Pi_F=h[-1]['Pi_F'],integration_seconds=r['integration_seconds'],identity_sha256=r['identity_sha256']))
    axes[0].set(xlabel='signed u',ylabel='signed v',title='Individual trajectories; no cross-sector interpolation')
    axes[1].set(xlabel='a',ylabel='Sigma_F',title='Frobenius shear magnitude');axes[2].set(xlabel='a',ylabel='Pi_F',title='Frobenius physical stress magnitude')
    for ax in axes:ax.grid(alpha=.25)
    fig.suptitle('Canonical frozen-resolution pilot: blue initial stress −, red +, gray zero\n○ actual initial, × final; distinct model from C15',fontsize=12);save(fig,'canonical_pilot')
    write_csv(ROOT/'data/results/pilot_summary.csv',summary);(ROOT/'data/results/pilot_summary.json').write_text(json.dumps(dict(completed=len(good),failed=len(results)-len(good),new_model_not_merged_with_C15=True,rows=summary),indent=2)+'\n')
if __name__=='__main__':c15();pilot()

def magnitude_grid():
    from matplotlib.lines import Line2D
    from matplotlib.colors import Normalize
    results=[json.loads(p.read_text()) for p in sorted((ROOT/'data/results/cases').glob('s*_p*.json'))]
    good=[r for r in results if r.get('status')=='completed']
    if not good:return
    fig,axes=plt.subplots(1,3,figsize=(15,5))
    colors={-1:'tab:blue',0:'gray',1:'tab:red'}
    for r in good:
        h=r['normalized_history'];color=colors[r['inputs']['stress_sign']]
        axes[0].plot([x['Sigma_F'] for x in h],[x['Pi_F'] for x in h],color=color,lw=.8,alpha=.7)
        axes[0].scatter(h[0]['Sigma_F'],h[0]['Pi_F'],facecolors='none',edgecolors=color,s=28,zorder=3)
        axes[0].scatter(h[-1]['Sigma_F'],h[-1]['Pi_F'],marker='x',color=color,s=23,zorder=3)
    legend=[Line2D([0],[0],color=colors[s],label=l) for s,l in [(-1,'initial stress −'),(1,'initial stress +'),(0,'initial Pi=0')]]
    legend += [Line2D([0],[0],marker='o',markerfacecolor='none',color='black',linestyle='none',label='actual initial'),Line2D([0],[0],marker='x',color='black',linestyle='none',label='final')]
    axes[0].legend(handles=legend,fontsize=8)
    axes[0].set(title='Actual magnitude trajectories: 28 unique cases',xlabel='Sigma_F',ylabel='Pi_F')
    norm=Normalize(vmin=min(r['final']['Sigma_F'] for r in good),vmax=max(r['final']['Sigma_F'] for r in good))
    for ax,sign in zip(axes[1:],[-1,1]):
        selected=[r for r in good if r['inputs']['stress_sign'] in (0,sign)]
        sc=ax.scatter([r['inputs']['Sigma_F'] for r in selected],[r['inputs']['Pi_F'] for r in selected],c=[r['final']['Sigma_F'] for r in selected],norm=norm,cmap='viridis',s=105,edgecolors='black',linewidths=.6)
        ax.set(title=f'Initial stress {"−" if sign<0 else "+"}: final Sigma_F',xlabel='requested initial Sigma_F',ylabel='requested initial Pi_F',xticks=[0,.01,.03,.06],yticks=[0,.0003,.0006,.0009])
        ax.ticklabel_format(axis='y',style='sci',scilimits=(-3,-3))
        ax.set_xlim(-.004,.064);ax.set_ylim(-.00007,.00097)
    cax=fig.add_axes([.935,.16,.012,.59])
    fig.colorbar(sc,cax=cax,label='final Sigma_F (common scale)')
    for ax in axes:ax.grid(alpha=.2)
    fig.suptitle('Frozen finite-resolution LRS canonical FV + gamma/nu hierarchy; same source and closure\nExact 4×4 input grids, no interpolation; four Pi=0 cases repeated in ± panels, 28 unique cases total',fontsize=11)
    fig.subplots_adjust(left=.06,right=.91,bottom=.13,top=.79,wspace=.36)
    for ext in ('png','svg','pdf'):fig.savefig(ROOT/'plots'/f'canonical_sigma_pi_grid.{ext}',dpi=170)
    plt.close(fig)

if __name__=='__main__':magnitude_grid()
