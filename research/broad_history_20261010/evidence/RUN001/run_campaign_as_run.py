"""Run the full declared interval; completed cases are identity-bound checkpoints."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import time
import numpy as np
import scipy
from model import default_config,history,summarize,BG_PATH,BG_SHA,HERE

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_json(path,value):
    path=Path(path); temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n'); os.replace(temp,path)

def cases():
    base=default_config(); out=[]
    for r in [0.,.01,-.01,.05,-.05,.1,-.1]:
        name='flrw' if r==0 else ('r'+('p' if r>0 else 'm')+str(abs(r)).replace('.',''))
        out.append((name,{**base,'r':r}))
    for key,values in [('fesc',[.1,.3]),('clumping',[2.,5.]),('T_K',[10000.,30000.]),('q_i',[.001])]:
        for value in values:out.append((f'{key}_{value:g}',{**base,key:value}))
    return out

def identity(config,n):
    return {'config':config,'nsteps':n,'model_sha256':sha(HERE/'model.py'),
            'runner_sha256':sha(__file__),'background_sha256':BG_SHA,
            'source_contract_sha256':sha(HERE/'EXTERNAL_SOURCE_CONTRACT.json')}

def execute_case(name,config,n,root,resume=True):
    folder=root/f'{name}_n{n}'; folder.mkdir(parents=True,exist_ok=True)
    ident=identity(config,n); done=folder/'COMPLETE.json'; data=folder/'history.npz'
    if done.exists() and resume:
        old=json.loads(done.read_text())
        if old['identity']!=ident or not data.exists() or sha(data)!=old['data_sha256']:
            raise RuntimeError(f'RESUME_IDENTITY_OR_DATA_MISMATCH:{folder}')
        return dict(np.load(data)),old
    if done.exists():raise RuntimeError('REFUSE_OVERWRITE_COMPLETED_CASE; use a new output directory')
    write_json(folder/'STARTED.json',{'identity':ident,'time_unix':time.time()})
    start=time.perf_counter(); h=history(config,n); elapsed=time.perf_counter()-start
    np.savez_compressed(data,**h)
    summary=summarize(h)
    if summary['max_photon_ledger_abs']/max(1,summary['Nemit'])>1e-10:
        raise RuntimeError('PHOTON_LEDGER_FAILURE')
    idx=np.unique(np.r_[np.arange(0,n+1,max(1,n//256)),n])
    names=list(h)
    np.savetxt(folder/'preview.csv',np.column_stack([h[k][idx] for k in names]),
               delimiter=',',header=','.join(names),comments='',fmt='%.16e')
    result={'status':'COMPUTED_SCOPED_NOT_YET_REVIEWED','identity':ident,
            'summary':summary,'wall_s':elapsed,'data_sha256':sha(data),
            'preview_sha256':sha(folder/'preview.csv')}
    write_json(done,result)
    print(f'{name} n={n} Qf={summary["Q_final"]:.6g} tau={summary["tau_20_to_4"]:.9g} wall={elapsed:.3f}s',flush=True)
    return h,result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args();root=args.output;root.mkdir(parents=True,exist_ok=True)
    results={}; trajectories={}; checks=[]
    for name,c in cases():
        for n in ([2048,4096,8192] if name in ('flrw','rp01') else [8192]):
            h,r=execute_case(name,c,n,root)
            results[f'{name}_n{n}']=r
            trajectories[(name,n)]=h
    for name in ['flrw','rp01']:
        fine=trajectories[(name,8192)];med=trajectories[(name,4096)];coarse=trajectories[(name,2048)]
        sf,sm=summarize(fine),summarize(med)
        metrics={'max_abs_Q':float(np.max(abs(fine['Q'][::2]-med['Q']))),
                 'delta_tau':abs(sf['tau_20_to_4']-sm['tau_20_to_4']),
                 'delta_z50':abs(sf['z50']-sm['z50']),'delta_z90':abs(sf['z90']-sm['z90'])}
        bounds={'max_abs_Q':1e-7,'delta_tau':1e-8,'delta_z50':1e-5,'delta_z90':1e-5}
        ratio=float(np.max(abs(coarse['Q']-med['Q'][::2]))/max(1e-30,metrics['max_abs_Q']))
        checks.append({'case':name,'kind':'whole_interval_refinement','metrics':metrics,'bounds':bounds,
                       'coarse_to_fine_Q_error_ratio':ratio,'pass':all(metrics[k]<=bounds[k] for k in metrics)})
    for mag in ['001','005','01']:
        p,m=trajectories[('rp'+mag,8192)],trajectories[('rm'+mag,8192)]
        difference=float(np.max(np.abs(p['Q']-m['Q'])))
        checks.append({'case':mag,'kind':'mean_volume_shear_parity','max_abs_Q':difference,
                       'max_abs_tau':float(np.max(abs(p['tau']-m['tau']))),'pass':difference<=1e-12})
    # Exactly zero background r reproduces the conventional R15 form. All cases use full interval.
    campaign={'claim':'reduced_filling_factor_mean_volume_history_only','redshift':[20,4],
        'helium_endpoint':'4+; singly ionized closure; no HeIII switch',
        'full_CR_RCT_HH_admission':'HOLD','python':platform.python_version(),
        'numpy':np.__version__,'scipy':scipy.__version__,'cases':results,'checks':checks,
        'status':'NUMERICAL_PASS_PENDING_REFERENCE_REVIEW' if all(c['pass'] for c in checks) else 'FAIL'}
    write_json(root/'CAMPAIGN.json',campaign)
    if campaign['status']=='FAIL':raise RuntimeError('PREDECLARED_CONVERGENCE_FAILED')
    plot(trajectories,root)

def plot(hs,root):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    b=hs[('flrw',8192)];fig,ax=plt.subplots(2,2,figsize=(11,8),constrained_layout=True)
    for name in ['fesc_0.1','fesc_0.3','clumping_2','clumping_5','T_K_10000','T_K_30000']:
        h=hs[(name,8192)];ax[0,0].plot(h['z'],h['Q'],color='.75',lw=1)
    ax[0,0].plot(b['z'],b['Q'],color='black',label='FLRW fiducial')
    ax[0,0].plot([],[],color='.75',label='One-at-a-time source / C / T scenarios')
    ax[0,0].set(ylabel='$Q_{\\rm HII}$',title='Broad history (fixed ionized-zone temperature)')
    for name,r in [('rp001',.01),('rp005',.05),('rp01',.1)]:
        h=hs[(name,8192)]
        ax[0,1].plot(h['z'],h['Q']-b['Q'],label=f'$s_i/H_i={r:g}$')
        ax[1,0].plot(h['z'],h['tau']-b['tau'],label=f'{r:g}')
    ax[0,1].set(ylabel='$Q_{\\rm Bianchi}-Q_{\\rm FLRW}$',title='Mean-expansion shear response')
    ax[1,0].set(ylabel='$\\Delta\\tau(20\\rightarrow \\bar z)$',title='Segment optical-depth response')
    for key,label in [('Nemit','Emitted'),('Nrec','Recombined'),('Nexcess','Unassigned after overlap')]:
        ax[1,1].plot(b['z'],b[key],label=label)
    ax[1,1].plot(b['z'],b['Q'],label='Ionized inventory')
    ax[1,1].set(ylabel='Effective photons per H nucleus',title='Fiducial photon budget')
    for a in ax.flat:a.set(xlim=(20,4),xlabel='Mean-volume redshift $\\bar z$');a.grid(alpha=.2);a.legend(fontsize=8)
    fig.suptitle('REI-ACCEL01: R15 + HG97-B, dust + $\\Lambda$ Bianchi I\nReduced model; no CR/RCT/thermal evolution; shear cases are not observationally admitted',fontsize=12)
    fig.savefig(root/'BROAD_HISTORY.png',dpi=180);fig.savefig(root/'BROAD_HISTORY.pdf')
    plt.close(fig)

if __name__=='__main__':main()
