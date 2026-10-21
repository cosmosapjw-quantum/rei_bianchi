#!/usr/bin/env python3
"""Component plots from actual saved tables; supports new NCP runs without old raw NPZ."""
import os
os.environ.setdefault('MPLCONFIGDIR','/tmp/rei-bianchi-component-mpl')
import argparse,csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
HERE=Path(__file__).resolve().parent

def read(path):return list(csv.DictReader(Path(path).open()))
def write(path,rows):
    with Path(path).open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def save(fig,path):
    fig.savefig(str(path)+'.png',dpi=180);fig.savefig(str(path)+'.pdf');plt.close(fig)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run',type=Path,required=True);ap.add_argument('--output',type=Path);ap.add_argument('--site-label',choices=['local','NCP'],default='local');a=ap.parse_args()
    out=a.output if a.output else a.run/'plots';out.mkdir(parents=True,exist_ok=False)
    matter=read(a.run/'matter_slice_with_reference_controls.csv')
    if len(matter)!=625:raise ValueError('600 actual new rows +25 reference controls required')
    zmax=max(float(r['Sigma']) for r in matter);heat=[]
    fig,axs=plt.subplots(2,2,figsize=(10.7,8.5),sharex=True,sharey=True,constrained_layout=True)
    for ax,(s,m) in zip(axs.flat,[(1,1),(1,-1),(-1,1),(-1,-1)]):
        grid=np.full((13,13),np.nan)
        for r in matter:
            if int(r['eps_sigma']) in (0,s) and int(r['eps_m']) in (0,m):
                i,j=int(r['sigma_index']),int(r['pi_m_index']);grid[j,i]=float(r['Sigma'])
                heat.append({'panel_eps_sigma':s,'panel_eps_m':m,'Sigma0':abs(float(r['signed_Sigma0'])),'Pi_m0':abs(float(r['signed_Pi_m0'])),'Sigma_end':r['Sigma'],'case_id':r['id'],'provenance':r['provenance'],'actual_signed_Pi_r0':r['signed_Pi_r0'],'actual_k':r['k']})
        if not np.isfinite(grid).all():raise ValueError('INCOMPLETE_MATTER_PANEL')
        im=ax.pcolormesh(np.linspace(0,.004,13),np.linspace(0,.0004,13),grid,shading='nearest',vmin=0,vmax=zmax,cmap='viridis')
        ax.set_xlim(0,.004);ax.set_ylim(0,.0004);ax.set_title(rf'$\epsilon_\sigma={s:+d},\ \epsilon_m={m:+d}$');ax.set_xlabel(r'Initial physical $\Sigma_0$');ax.set_ylabel(r'Initial physical $\Pi_{m0}$');ax.ticklabel_format(axis='both',style='sci',scilimits=(0,0))
    fig.colorbar(im,ax=axs,label=r'Final physical $\Sigma$ at $\bar z=4$',shrink=.9)
    fig.suptitle(f'Matter-stress companion slice: preliminary {a.site_label} results\n600 new coupled trajectories (initial radiation k=0) +25 historical reference controls')
    save(fig,out/'matter_sigma_end_heatmaps');write(out/'matter_heatmap_plot_data.csv',heat)
    old=read(HERE/'old_representative_histories.csv');selected=['s12_+1_p12_+1','s12_+1_p12_-1','s12_+1_p00_+0','s00_+0_p12_+1']
    fig,axs=plt.subplots(2,2,figsize=(11.5,7.5),constrained_layout=True)
    titles=[r'$S_0=+.004,\ \widetilde\Pi_{r0}=+.001$',r'$S_0=+.004,\ \widetilde\Pi_{r0}=-.001$',r'$S_0=+.004,\ \Pi_{r0}\simeq0$',r'$S_0=0,\ \widetilde\Pi_{r0}=+.001$']
    for ax,cid,title in zip(axs.flat,selected,titles):
        rows=[r for r in old if r['case_id']==cid];z=[float(r['zbar']) for r in rows]
        for key,label,color,ls in [('signed_Pi_m',r'matter $\widetilde\Pi_m$','tab:blue','-'),('signed_Pi_r',r'radiation $\widetilde\Pi_r$','tab:orange','-'),('signed_Pi_total',r'total signed $\widetilde\Pi_{tot}$','black','--')]:ax.plot(z,[float(r[key]) for r in rows],label=label,color=color,ls=ls,lw=1.6)
        ax.set_yscale('symlog',linthresh=1e-9);ax.set_xlim(20,4);ax.set_xlabel(r'Mean redshift $\bar z$');ax.set_ylabel('Signed dimensionless component stress');ax.set_title(title);ax.grid(alpha=.22)
    axs.flat[0].legend(fontsize=8);fig.suptitle('Original local pilot: initially matter-isotropic histories, decomposed without ODE rerun\nCommon orthonormal normal frame; symlog y scale (linear within ±10⁻⁹)')
    save(fig,out/'old_history_component_decomposition');write(out/'old_history_component_plot_data.csv',old)
    endpoints=read(a.run/'endpoints.csv');mixed=[r for r in endpoints if r['lane']=='MIXED_CANCELLATION'];plotrows=[]
    fig,axs=plt.subplots(3,2,figsize=(12,10),constrained_layout=True)
    for rowindex,s0 in enumerate((0.,.004,-.004)):
        cases=[r for r in mixed if float(r['signed_Sigma0'])==s0]
        for c in sorted(cases,key=lambda r:float(r['signed_Pi_m0'])):
            sign=int(c['eps_m']);ls='-' if sign>0 else '--';cid=c['id']
            with np.load(a.run/'cases'/(cid+'.npz')) as d:
                z=d['zbar'];axs[rowindex,0].plot(z,d['Sigma'],ls=ls,label=rf'$\widetilde\Pi_{{m0}}={sign:+d}\times.0004$',color='tab:green' if sign>0 else 'tab:purple')
                axs[rowindex,1].plot(z,d['signed_Pi_m'],ls=ls,color='tab:blue',label=rf'matter, initial sign {sign:+d}')
                axs[rowindex,1].plot(z,d['signed_Pi_r'],ls=ls,color='tab:orange',label=rf'radiation, initial matter sign {sign:+d}')
                axs[rowindex,1].plot(z,d['signed_Pi_total'],ls=ls,color='black',lw=1,label=rf'signed total, initial matter sign {sign:+d}')
                keys=('x','zbar','Sigma','s_over_H','signed_Pi_m','signed_Pi_r','signed_Pi_total','Pi_total','p_m_J_m3','p_r_J_m3','b','E0','E2')
                for i in range(len(z)):plotrows.append({'case_id':cid,'signed_Sigma0':s0,'signed_Pi_m0':c['signed_Pi_m0'],'signed_Pi_r0':c['signed_Pi_r0'],**{k:float(d[k][i]) for k in keys}})
        axs[rowindex,0].set_ylabel(r'Physical shear magnitude $\Sigma$');axs[rowindex,0].set_title(rf'Initial signed $S_0={s0:+.3f}$')
        axs[rowindex,1].set_ylabel(r'Signed $\widetilde\Pi_X$');axs[rowindex,1].axhline(0,color='grey',lw=.6);axs[rowindex,1].set_title('Actual coupled component histories')
        for ax in axs[rowindex]:ax.set_xlim(20,4);ax.set_xlabel(r'Mean redshift $\bar z$');ax.grid(alpha=.2);ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
    axs[0,0].legend(fontsize=8);axs[0,1].legend(fontsize=7,ncol=2)
    fig.suptitle(f'Mixed cancellation: six new coupled {a.site_label} trajectories\n'+r'$\widetilde\Pi_{m0}=-\widetilde\Pi_{r0}=\pm.0004$; total magnitude $=|\widetilde\Pi_m+\widetilde\Pi_r|$')
    save(fig,out/'mixed_cancellation_components_sigma');write(out/'mixed_cancellation_plot_data.csv',plotrows)
    summary={'matter_table_rows':625,'new_matter_ODE':600,'reference_controls':25,'mixed_new_ODE':6,'site_label_new_run':a.site_label,'old_component_plot_source':'historical local625; no rerun','mixed_endpoints':mixed}
    (out/'plot_summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
