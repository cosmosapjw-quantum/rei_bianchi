#!/usr/bin/env python3
"""Figures from already completed source-bound histories; no integration calls."""
import argparse,json,csv,hashlib
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import cumulative_simpson

def main(root, display=True):
    root=Path(root);out=root/'results/figures';out.mkdir(parents=True,exist_ok=False)
    p=root/'packet/long.npz';idx=json.loads((root/'packet/INDEX.json').read_text())
    assert hashlib.sha256(p.read_bytes()).hexdigest()==idx['datasets']['long']['sha256']
    with np.load(p,allow_pickle=False) as z:
        ids=z['case_ids'];x=z['x'];v=z['values'];j=list(ids).index('mixed_s+0_m+1');a=v[j]
    H,S,pm,pr=a[:4];zbar=21*np.exp(-x)-1;root2=np.sqrt(2)
    # Same saved path: no counterfactual removal of either species.
    pref=np.exp(-3*x)/H
    mm=pref*cumulative_simpson(np.exp(3*x)*H*pm,x=x,initial=0)
    mr=pref*cumulative_simpson(np.exp(3*x)*H*pr,x=x,initial=0)
    ini=pref*H[0]*S[0]
    fig,ax=plt.subplots(figsize=(8.2,5.3),layout='constrained')
    ax.plot(zbar,root2*abs(pm),label=r'$\Pi_m$ (massive matter)',linewidth=2)
    ax.plot(zbar,root2*abs(pr),label=r'$\Pi_r$ (photons + massless neutrinos)',linewidth=2,linestyle='--')
    ax.set(xlabel=r'Mean redshift $\bar z$',ylabel='Full Frobenius stress magnitude',
           title='Separate stresses on an initially cancelling path')
    ax.invert_xaxis();ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend()
    fig.savefig(out/'separate_stress_magnitudes.png',dpi=180,bbox_inches='tight');plt.show() if display else plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,5.3),layout='constrained')
    ax.plot(zbar,root2*mm,label='Matter history contribution',linewidth=2)
    ax.plot(zbar,root2*mr,label='Radiation history contribution',linewidth=2,linestyle='--')
    ax.plot(zbar,root2*S,label='Observed signed shear',linewidth=2,linestyle='-.')
    ax.plot(zbar,root2*(ini+mm+mr),label='Sum of path contributions',linewidth=1,linestyle=':')
    ax.set(xlabel=r'Mean redshift $\bar z$',ylabel=r'Signed full-Frobenius amplitude',title='Shear retains the two stress histories separately')
    ax.invert_xaxis();ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0));ax.legend()
    fig.savefig(out/'separate_shear_memory.png',dpi=180,bbox_inches='tight');plt.show() if display else plt.close(fig)
    with (root/'results/memory/long_memory.csv').open() as f: rows=list(csv.DictReader(f))
    chosen=[r for r in rows if r['case_id'].startswith('m_s00_')]
    chosen.sort(key=lambda r:float(r['initial_P_m_h']))
    fig,ax=plt.subplots(figsize=(8.2,5.3),layout='constrained')
    xx=[root2*float(r['initial_P_m_h']) for r in chosen]
    ax.plot(xx,[float(r['matter_memory_F']) for r in chosen],marker='o',label='Matter contribution')
    ax.plot(xx,[float(r['radiation_memory_F']) for r in chosen],marker='s',label='Induced radiation contribution')
    ax.plot(xx,[float(r['observed_signed_shear_F']) for r in chosen],linestyle='--',label='Final signed shear')
    ax.set(xlabel=r'Initial signed $\Pi_{m,F}$',ylabel='Final signed full-Frobenius shear contribution',title=r'Matter-stress slice: $\Sigma_0=0$, initial $\Pi_r\simeq0$')
    ax.ticklabel_format(axis='both',style='sci',scilimits=(0,0));ax.legend()
    fig.savefig(out/'matter_slice_memory.png',dpi=180,bbox_inches='tight');plt.show() if display else plt.close(fig)
    table={'zbar':zbar,'S_F':root2*S,'Pi_m_F':root2*abs(pm),'Pi_r_F':root2*abs(pr),'memory_m_F':root2*mm,'memory_r_F':root2*mr,'memory_initial_F':root2*ini}
    with (out/'cancellation_plot_data.csv').open('x',newline='') as f:
        w=csv.writer(f);w.writerow(table);w.writerows(zip(*table.values()))
    data={'case':'mixed_s+0_m+1','source_packet_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
          'normalization':'Full Frobenius for all figures; sqrt(2) times source half-contraction coordinates',
          'source_lane':'REI198 collisionless long; NOT REI213 short warm HHe/UV',
          'figure_data':'cancellation_plot_data.csv and results/memory/long_memory.csv',
          'end_memory_m_F':float(root2*mm[-1]),'end_memory_r_F':float(root2*mr[-1]),'end_S_F':float(root2*S[-1]),
          'plots':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.glob('*.png')}}
    (out/'FIGURE_RECEIPT.json').write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();main(a.root)
