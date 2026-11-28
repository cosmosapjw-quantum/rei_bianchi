"""Saved-data species decomposition; no solver calls.

LRS pi_ab=diag(-pi_s,-pi_s,2pi_s). Matter and radiation signed
pi_s add before the Frobenius magnitude. C15 stores deltaP=3pi_s;
canonical stores pi_s directly. Isotropic dust/gas has zero tracefree
stress in these closures. Current canonical data is an initial Pi_m=0
slice of (Sigma_F,Pi_m,Pi_r), not an independent three-parameter sweep.
"""
from pathlib import Path
import json,csv,math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coordinates import normalized
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'svg.fonttype':'none','font.size':10})

def components(H,s,matter,gamma,nu,uv=0.):
    v=lambda p:normalized(H,s,[p])['v']
    vm,vg,vn,vu=map(v,(matter,gamma,nu,uv));vr=vg+vn+vu;vt=vm+vr
    return dict(Sigma_F=normalized(H,s,[])['Sigma_F'],v_m=vm,v_r=vr,v_gamma=vg,v_nu=vn,v_UV=vu,Pi_m=abs(vm),Pi_r=abs(vr),v_total=vt,Pi_total=abs(vt),chi_mr=int(vm*vr>0)-int(vm*vr<0))

def canonical_row(d):return components(d['H'],d['s'],d['Pi_matter_J_m3'],d['Pi_gamma_J_m3'],d['Pi_nu_J_m3'])
def c15_row(d):return components(d['H'],d['s_inv_s'],d['Pi_massive']/3,d['Pi_gamma']/3,d['Pi_nu']/3,d['Pi_UV']/3)

def save(fig,name):
    fig.tight_layout()
    for ext in ('png','svg','pdf'):fig.savefig(ROOT/'plots'/f'{name}.{ext}',dpi=170)
    plt.close(fig)

def table(name,rows):
    p=ROOT/'data/results'/name
    p.with_suffix('.json').write_text(json.dumps(rows,indent=2)+'\n')
    with p.with_suffix('.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def execute():
    allrows=[];ends=[];fig,axes=plt.subplots(1,3,figsize=(14,5));signed,saxes=plt.subplots(1,2,figsize=(11,4.6));colors={-1:'tab:blue',0:'gray',1:'tab:red'};diff=[];initialm=[]
    for p in sorted((ROOT/'data/results/cases').glob('s*_p*.json')):
        case=json.loads(p.read_text());h=[dict(case_id=case['case_id'],saved_index=i,a=d['a'],initial_stress_sign=case['inputs']['stress_sign'],**canonical_row(d)) for i,d in enumerate(case['diagnostics'])];allrows+=h;ends.extend([dict(endpoint=ep,**row) for ep,row in [('initial',h[0]),('final',h[-1])]]);color=colors[case['inputs']['stress_sign']];initialm.append(h[0]['Pi_m'])
        diff.extend(abs(r['v_total']-old['v']) for r,old in zip(h,case['normalized_history']))
        for ax,x,y in [(axes[0],'Sigma_F','Pi_m'),(axes[1],'Sigma_F','Pi_r'),(axes[2],'Pi_m','Pi_r')]:
            ax.plot([r[x] for r in h],[r[y] for r in h],color=color,alpha=.65,lw=.8);ax.scatter(h[0][x],h[0][y],facecolors='none',edgecolors=color,s=22);ax.scatter(h[-1][x],h[-1][y],marker='x',color=color,s=20)
        for ax,key in zip(saxes,['v_m','v_r']):ax.plot([r['a'] for r in h],[r[key] for r in h],color=color,alpha=.65,lw=.8)
    for ax,x,y in [(axes[0],'Sigma_F','Pi_m'),(axes[1],'Sigma_F','Pi_r'),(axes[2],'Pi_m','Pi_r')]:ax.set(xlabel=x,ylabel=y);ax.grid(alpha=.25)
    fig.suptitle('Canonical initial Pi_m≈0 slice: 28 cases, fixed finite-resolution LRS closure\nBlue initial radiation −, red +, gray zero; ○ initial, × final; no cross-case interpolation',fontsize=11);save(fig,'canonical_species_stress')
    for ax,key in zip(saxes,['v_m','v_r']):ax.set(xlabel='a',ylabel=key);ax.axhline(0,color='black',lw=.5);ax.grid(alpha=.25)
    signed.suptitle('Signed matter / radiation stress: cancellation retained before total magnitude\nSame 28-case initial Pi_m≈0 slice; blue −, red +, gray zero radiation sector',fontsize=11);save(signed,'canonical_species_signed')
    table('canonical_species_stress',allrows);table('canonical_species_endpoints',ends)
    saved=json.loads((ROOT/'data/original/C15_STUDY_RESULTS.json').read_text());crows=[];cends=[];cf,cax=plt.subplots(1,2,figsize=(12,5));cdiff=[]
    for series in saved['series']:
        name=series['scientific_case'];control=name=='GRAVITY_PI_DISABLED_CONTROL';h=[dict(series=name,control=control,saved_index=i,a=d['a'],**c15_row(d)) for i,d in enumerate(series['history'])];crows+=h;cends.extend([dict(endpoint=ep,**row) for ep,row in [('first_saved_post_step',h[0]),('final',h[-1])]])
        for row,d in zip(h,series['history']):cdiff.append(abs(row['v_total']-normalized(d['H'],d['s_inv_s'],[(d['Pi_massive']+d['Pi_gamma']+d['Pi_nu']+d['Pi_UV'])/3])['v']))
        ax=cax[int(control)];line=ax.plot([r['v_m'] for r in h],[r['v_r'] for r in h],label=name)[0];ax.scatter(h[0]['v_m'],h[0]['v_r'],facecolors='none',edgecolors=line.get_color());ax.scatter(h[-1]['v_m'],h[-1]['v_r'],marker='x',color=line.get_color())
    for ax,title in zip(cax,['Seven physical saved series','Gravity-source-disabled control']):
        ax.set(title=title,xlabel='signed v_m (massive)',ylabel='signed v_r (gamma + nu + UV)');ax.set_xscale('symlog',linthresh=1e-12);ax.set_yscale('symlog',linthresh=1e-12);ax.grid(alpha=.25);ax.legend(fontsize=7)
    cf.suptitle('C15 distinct native H/He model: physical stress decomposition\n○ first saved post-step, × final; disabled gravity source does not erase physical stress',fontsize=11);save(cf,'c15_species_stress');table('c15_species_stress',crows);table('c15_species_endpoints',cends)
    summary=dict(canonical_rows=len(allrows),canonical_cases=28,c15_rows=len(crows),c15_series=8,canonical_endpoint_rows=len(ends),c15_endpoint_rows=len(cends),max_canonical_signed_linear_sum_difference=max(diff),max_c15_signed_linear_sum_difference=max(cdiff),max_initial_canonical_Pi_m=max(initialm),canonical_scope='initial Pi_m approximately zero slice, not independent three-parameter grid',Pi_total_definition='abs(v_m+v_r); differs from Pi_m+Pi_r for opposite signs',C15_UV_classification='radiation',science_integrations=0)
    (ROOT/'data/results/species_stress_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':execute()

def render_c15_saved():
    """Presentation-only regeneration from the derived C15 table."""
    rows=json.loads((ROOT/'data/results/c15_species_stress.json').read_text())
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    from matplotlib.ticker import NullFormatter
    for name in dict.fromkeys(r['series'] for r in rows):
        h=[r for r in rows if r['series']==name];ax=axes[int(h[0]['control'])];line=ax.plot([r['v_m'] for r in h],[r['v_r'] for r in h],label=name)[0];ax.scatter(h[0]['v_m'],h[0]['v_r'],facecolors='none',edgecolors=line.get_color());ax.scatter(h[-1]['v_m'],h[-1]['v_r'],marker='x',color=line.get_color())
    for ax,title in zip(axes,['Seven physical saved series','Gravity-source-disabled control']):
        ax.set(title=title,xlabel='signed v_m (massive)',ylabel='signed v_r (gamma + nu + UV)');ax.set_xscale('symlog',linthresh=1e-12);ax.set_yscale('symlog',linthresh=1e-12);ax.set_xticks([-1e-3,-1e-6,0,1e-6,1e-3]);ax.xaxis.set_minor_formatter(NullFormatter());ax.grid(alpha=.25);ax.legend(fontsize=7)
    fig.suptitle('C15 distinct native H/He model: physical stress decomposition\n○ first saved post-step, × final; disabled gravity source does not erase physical stress',fontsize=11);save(fig,'c15_species_stress')
