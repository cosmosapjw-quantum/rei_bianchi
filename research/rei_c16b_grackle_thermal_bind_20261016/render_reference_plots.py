"""Render the preserved fixed-geometry local-cell trajectories, without reruns."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'evidence/reference'
def main():
    summaries=json.loads((OUT/'trajectory_summary.json').read_text())
    fig,axes=plt.subplots(3,3,figsize=(13.0,9.0),constrained_layout=True)
    colors=['#2468a0','#b54e23','#497c40']
    for col,name in enumerate(['recomb8000','collision1e5','mixed1e4']):
        entry=next(v for v in summaries if v['case']==name)
        comparison=entry['comparisons'][-1]
        native=[json.loads(l) for l in Path(comparison['native_history_path']).read_text().splitlines()]
        ref=json.loads((OUT/(name+'_radau.json')).read_text());r=np.array(ref['history']);tn=np.array([v['time_s'] for v in native])/3.15576e13;tr=r[:,0]/3.15576e13
        n_h=native[0]['nh'];n_he=native[0]['nhe'];kb=1.380649e-16
        ne=n_h*r[:,1]+n_he*(r[:,2]+2*r[:,3]);temperature=2*n_h*r[:,4]/(3*kb*(n_h+n_he+ne))
        axes[0,col].plot(tn,[v['temperature'] for v in native],color=colors[0],lw=1.4)
        axes[0,col].plot(tr,temperature,color='black',ls='--',lw=1.1)
        fractions=np.array([v['fractions'] for v in native]);cell=native[0]['transport_cells'];photons=np.array([[sum(v['photons'][i*cell:(i+1)*cell]) for i in range(3)] for v in native])
        for j,color in enumerate(colors):
            axes[1,col].plot(tn,fractions[:,j],color=color,lw=1.2)
            axes[1,col].plot(tr,r[:,1+j],color=color,ls='--',lw=1.)
            axes[2,col].plot(tn,photons[:,j],color=color,lw=1.2)
            axes[2,col].plot(tr,r[:,5+j],color=color,ls='--',lw=1.)
        axes[0,col].set_title(f"{name}: native BE n={comparison['n']}",fontsize=11)
        for row in range(3):axes[row,col].grid(alpha=.22);axes[row,col].ticklabel_format(axis='x',style='sci',scilimits=(-2,3))
        axes[2,col].set_xlabel('Elapsed proper time [Myr]')
    axes[0,0].set_ylabel('Gas temperature [K]')
    axes[1,0].set_ylabel('Species fraction [H/H or He/He]')
    axes[2,0].set_ylabel('Photon number [per H]')
    axes[1,2].legend([Line2D([],[],color=c) for c in colors],['H II / H','He II / He','He III / He'],fontsize=8)
    axes[2,2].legend([Line2D([],[],color=c) for c in colors],['20 eV','40 eV','80 eV'],fontsize=8)
    axes[0,2].legend([Line2D([],[],color='black'),Line2D([],[],color='black',ls='--')],['Original native backward Euler','Independent C-rate/Python Radau'],fontsize=8)
    fig.suptitle('Local H/He–photon kinetics with all native Grackle Case-A terms\nFixed a=0.1, nH=1.89820×10⁻⁴ cm⁻³, TCMB=27.255 K; no cosmological evolution',fontsize=13)
    for suffix in ['png','pdf']:fig.savefig(OUT/f'fixed_cell_histories.{suffix}',dpi=180)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.3,4.7),constrained_layout=True)
    for name,color in zip(['recomb8000','collision1e5','mixed1e4'],colors):
        entries=next(v for v in summaries if v['case']==name)['comparisons'];n=[v['n'] for v in entries]
        ax.loglog(n,[v['max_fixed_t32_observation_error'] for v in entries],'-o',color=color,label=name+' fixed observations')
        ax.loglog(n,[v['endpoint_error'] for v in entries],'--',color=color,alpha=.8)
    ax.axhline(.005,color='black',ls=':',label='Frozen state-norm target 0.005')
    ax.set(xlabel='Native time steps over the unchanged horizon',ylabel='Physical state error norm',title='Temporal refinement against independent C-backed Radau\nSolid: original 33 observation times; dashed: endpoint')
    ax.grid(alpha=.25,which='both');ax.legend(fontsize=8)
    for suffix in ['png','pdf']:fig.savefig(OUT/f'temporal_refinement.{suffix}',dpi=180)
    plt.close(fig)
    print('Rendered fixed_cell_histories and temporal_refinement PNG/PDF from preserved raw trajectories.')
if __name__=='__main__':main()
