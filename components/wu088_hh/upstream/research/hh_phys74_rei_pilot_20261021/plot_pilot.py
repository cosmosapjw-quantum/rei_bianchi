"""Source-bound preliminary CONTROL figures, without fitted curves or speed claims."""
from __future__ import annotations
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np

def read_cases(out):
    identity=json.loads((out/'IDENTITY.json').read_text())
    canonical=lambda x:(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode()
    pin=hashlib.sha256(canonical(identity)).hexdigest();rows=[];cases=[]
    for p in sorted((out/'cases').glob('case-*.json')):
        obj=json.loads(p.read_text());r=obj['result'];q=r['request']
        if obj['identity_sha256']!=pin or hashlib.sha256(canonical(r)).hexdigest()!=obj['result_sha256']:raise ValueError('result binding mismatch')
        a=r['history'][0];b=r['history'][-1]
        if not all(np.isfinite([z['Sigma_F'],z['Pi_F'],z['H_per_s'],z['b']]).all() for z in r['history']):raise ValueError('nonfinite result')
        rows.append(dict(case_id=q['case_id'],Sigma0_signed=q['Sigma0_signed'],Pi0_signed=q['Pi0_signed'],
          Sigma0=a['Sigma_F'],Pi0=a['Pi_F'],Sigma_end=b['Sigma_F'],Pi_end=b['Pi_F'],
          Sigma_end_signed=b['Sigma_signed'],Pi_end_signed=b['Pi_signed'],b_end=b['b'],
          E2_gamma_end=b['E2_gamma'],nfev=r['diagnostics']['nfev']))
        cases.append(r)
    return rows,cases


def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);ap.add_argument('--figures',required=True,type=Path);a=ap.parse_args(argv)
    rows,cases=read_cases(a.out);a.figures.mkdir(parents=True,exist_ok=True)
    with (a.figures/'PILOT_SUMMARY.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    import matplotlib.pyplot as plt
    sigma=sorted({r['Sigma0_signed'] for r in rows if r['Sigma0_signed']>=0})
    pi=sorted({abs(r['Pi0_signed']) for r in rows})
    limits=[min(r['Sigma_end_signed'] for r in rows if r['Sigma0_signed']>=0)*1000,max(r['Sigma_end_signed'] for r in rows if r['Sigma0_signed']>=0)*1000]
    for stress_sign,tag in [(1,'aligned'),(-1,'opposed')]:
        values=np.full((len(pi),len(sigma)),np.nan)
        for r in rows:
            if r['Sigma0_signed']>=0 and stress_sign*r['Pi0_signed']>=0:
                values[pi.index(abs(r['Pi0_signed'])),sigma.index(r['Sigma0_signed'])]=r['Sigma_end_signed']
        fig,ax=plt.subplots(figsize=(8,5.5),layout='constrained')
        m=ax.pcolormesh(np.array(sigma)*1000,np.array(pi)*1000,values*1000,shading='nearest',vmin=limits[0],vmax=limits[1])
        for j,y in enumerate(pi):
            for i,x in enumerate(sigma):
                ax.text(x*1000,y*1000,f'{values[j,i]*1000:.3f}',ha='center',va='center',fontsize=8,
                        bbox=dict(boxstyle='round,pad=0.15',alpha=.65))
        ax.set_xticks(np.array(sigma)*1000);ax.set_yticks(np.array(pi)*1000)
        ax.set_xlim(-.16,4.35);ax.set_ylim(-.06,1.09)
        ax.set_xlabel(r'Initial $\Sigma_0=\|\sigma\|_F/H$  [$10^{-3}$]')
        ax.set_ylabel(r'Initial $\Pi_0=\kappa_t\|\pi\|_F/H^2$  [$10^{-3}$]')
        ax.set_title(f'LRS Bianchi I control: {tag} initial stress\n'+r'$z:20\to4$; collisionless $\gamma+\nu+$ massive species',fontsize=12)
        fig.colorbar(m,ax=ax,label=r'Signed final $\sqrt{6}s/H$  [$10^{-3}$]')
        fig.suptitle('PRELIMINARY: no H/He chemistry or ionizing source',fontsize=10)
        fig.savefig(a.figures/f'SIGMA_PI_{tag}.png',dpi=160)
        plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,5.5),layout='constrained')
    for r in cases:
        q=r['request']
        if (q['Sigma0_signed'],q['Pi0_signed']) in [(0.,.001),(.001,0.),(.001,.001),(.001,-.001),(.004,.001)]:
            h=r['history'];ax.plot([z['Sigma_F'] for z in h],[z['Pi_F'] for z in h],marker='o',markevery=[0],label=f"S0={q['Sigma0_signed']:g}, P0={q['Pi0_signed']:g}")
    ax.set_xlabel(r'$\Sigma=\|\sigma\|_F/H$');ax.set_ylabel(r'$\Pi=\kappa_t\|\pi\|_F/H^2$')
    ax.set_title('Preliminary collisionless LRS Bianchi I trajectories\n'+r'$z:20\to4$; circles mark initial states')
    ax.legend(fontsize=8);fig.savefig(a.figures/'SIGMA_PI_trajectories.png',dpi=160);plt.close(fig)
    summary=dict(cases=len(rows),points_per_history=len(cases[0]['history']),
        max_initial_coordinate_error=max(r['diagnostics']['initial_coordinate_abs_error'] for r in cases),
        max_massless_number_error=max(r['diagnostics']['max_number_error'] for r in cases),
        max_algebraic_H_constraint=max(r['diagnostics']['max_algebraic_H_constraint_relative'] for r in cases),
        min_cell_number=min(r['diagnostics']['min_cell_number'] for r in cases),
        final_Sigma_range=[min(r['Sigma_end'] for r in rows),max(r['Sigma_end'] for r in rows)],
        final_Pi_range=[min(r['Pi_end'] for r in rows),max(r['Pi_end'] for r in rows)],
        signed_final_shear_reversals=sum(r['Sigma0_signed']*r['Sigma_end_signed']<0 for r in rows),
        total_nfev=sum(r['nfev'] for r in rows),benchmark_runs=0,
        claim='EXECUTED_PRELIMINARY_COLLISIONLESS_CONTROL_ONLY',NCP_run=False,
        HHe_feedback=False,continuum_error_certified=False,HH_R10='OFF')
    (a.figures/'SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
