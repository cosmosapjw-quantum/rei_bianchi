#!/usr/bin/env python3
"""Plot only completed pilot raw histories/endpoints; preserve exact plot tables."""
import argparse,csv,json,os
os.environ.setdefault('MPLCONFIGDIR','/tmp/rei-bianchi-mpl-cache')
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--output',type=Path);ap.add_argument('--site-label',choices=['local','NCP'],default='local');a=ap.parse_args()
    rows=list(csv.DictReader((a.run/'endpoints.csv').open()))
    if len(rows)!=625:raise ValueError('heatmap requires complete 625-case table')
    out=a.output if a.output else a.run/'plots';out.mkdir(exist_ok=False)
    zmax=max(float(r['Sigma']) for r in rows)
    fig,axs=plt.subplots(2,2,figsize=(10.6,8.2),constrained_layout=True,sharex=True,sharey=True)
    heat=[]
    for ax,(s,t) in zip(axs.flat,[(1,1),(1,-1),(-1,1),(-1,-1)]):
        grid=np.full((13,13),np.nan)
        for r in rows:
            if int(r['eps_sigma']) in (0,s) and int(r['eps_pi']) in (0,t):
                i,j=int(r['sigma_index']),int(r['pi_index']);grid[j,i]=float(r['Sigma'])
                heat.append({'eps_sigma_panel':s,'eps_pi_panel':t,'Sigma0':r['Sigma0'],'Pi0':r['Pi0'],'Sigma_end':r['Sigma'],'case_id':r['id']})
        if not np.isfinite(grid).all():raise ValueError('incomplete physical-axis panel')
        image=ax.pcolormesh(np.linspace(0,.004,13),np.linspace(0,.001,13),grid,shading='nearest',cmap='viridis',vmin=0,vmax=zmax,rasterized=True)
        ax.set_xlim(0,.004);ax.set_ylim(0,.001)
        ax.set_title(rf'$\epsilon_\sigma={s:+d},\ \epsilon_\pi={t:+d}$');ax.set_xlabel(r'Initial physical $\Sigma_0$');ax.set_ylabel(r'Initial physical $\Pi_0$');ax.ticklabel_format(axis='both',style='sci',scilimits=(0,0))
    fig.colorbar(image,ax=axs,label=r'Final $\Sigma=\sqrt{3}|s|/H$ at $\bar z=4$',shrink=.9)
    fig.suptitle(f'Self-gravitating collisionless LRS slice: preliminary {a.site_label} pilot\n625 signed initial conditions; physical magnitude axes')
    fig.savefig(out/'sigma_end_heatmaps.png',dpi=190);fig.savefig(out/'sigma_end_heatmaps.pdf');plt.close(fig)
    with (out/'heatmap_plot_data.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(heat[0]));w.writeheader();w.writerows(heat)
    fig,axs=plt.subplots(1,2,figsize=(11.3,4.7),constrained_layout=True);history=[]
    selected=[('s00_+0_p00_+0','isotropic control'),('s12_+1_p12_+1',r'$\epsilon_\sigma=+1,\epsilon_\pi=+1$'),('s12_+1_p12_-1',r'$\epsilon_\sigma=+1,\epsilon_\pi=-1$'),('s12_-1_p12_+1',r'$\epsilon_\sigma=-1,\epsilon_\pi=+1$'),('s12_-1_p12_-1',r'$\epsilon_\sigma=-1,\epsilon_\pi=-1$')]
    for cid,label in selected:
        d=np.load(a.run/'cases'/(cid+'.npz'))
        for ax,k in zip(axs,('Sigma','Pi')):ax.plot(d['zbar'],d[k],label=label,lw=1.8)
        for i in range(len(d['x'])):history.append({'case_id':cid,**{k:float(d[k][i]) for k in ('x','zbar','elapsed_seconds','Sigma','Pi','signed_Pi','s_over_H','b','E0','E2')}})
    for ax,k in zip(axs,('Sigma','Pi')):
        ax.set_xlim(20,4);ax.set_xlabel(r'Mean redshift $\bar z$');ax.set_ylabel('$'+('\\Sigma' if k=='Sigma' else '\\Pi')+r'(\bar z)$');ax.grid(alpha=.23);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axs[0].legend(fontsize=8);fig.suptitle(r'Physical tensor magnitudes: $\Sigma_0=0.004$, $\Pi_0=0.001$ corners + isotropic control'+'\nCollisionless LRS, half-contraction norm; no native H/He feedback')
    fig.savefig(out/'sigma_pi_evolution.png',dpi=190);fig.savefig(out/'sigma_pi_evolution.pdf');plt.close(fig)
    with (out/'representative_history_plot_data.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(history[0]));w.writeheader();w.writerows(history)
    summary={'case_count':len(rows),'max_initial_axis_error':max(float(r['axis_error']) for r in rows),'max_abs_k':max(abs(float(r['k'])) for r in rows),'Sigma_end_min':min(float(r['Sigma']) for r in rows),'Sigma_end_max':zmax,'minimum_sampled_angular_brightness':min(float(r['minimum_sampled_angular_brightness']) for r in rows),'corner_endpoints':[r for r in rows if int(r['sigma_index'])==12 and int(r['pi_index'])==12]}
    (out/'plot_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
