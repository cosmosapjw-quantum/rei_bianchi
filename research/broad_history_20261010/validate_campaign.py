"""Focused full-interval comparison with a separately implemented adaptive IVP."""
from pathlib import Path
import hashlib,json,time
import numpy as np
from model import HERE,summarize,C_CM_S,SIGMA_T_CM2
from reference import run_reference

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    root=HERE/'evidence/RUN002';results=[];outputs=[]
    for name,r in [('flrw',0.),('rp01',.1)]:
        folder=root/f'{name}_n16384';record=json.loads((folder/'COMPLETE.json').read_text())
        data=folder/'history.npz'
        if sha(data)!=record['data_sha256']:raise RuntimeError('PRIMARY_DATA_MISMATCH')
        h=dict(np.load(data)); ref=run_reference({'r':r},epochs=h['x'])
        rh=ref.pop('history');q=np.array([p['Q'] for p in rh]);tau=np.array([p['tau'] for p in rh])
        s=summarize(h);o=ref['observables']
        metrics={'max_abs_Q':float(np.max(abs(h['Q']-q))),
                 'max_abs_tau':float(np.max(abs(h['tau']-tau))),
                 'delta_z50':abs(s['z50']-o['z50']),'delta_z90':abs(s['z90']-o['z90'])}
        limits={'max_abs_Q':1e-7,'max_abs_tau':1e-8,'delta_z50':1e-5,'delta_z90':1e-5}
        out=root/f'{name}_reference_fine.npz';np.savez_compressed(out,x=h['x'],Q=q,tau=tau)
        results.append({'case':name,'comparison':metrics,'limits':limits,
            'pass':all(metrics[k]<=limits[k] for k in metrics),'reference':ref,
            'primary_data_sha256':sha(data),'reference_data_sha256':sha(out)})
        # Export a new, explicitly reduced-model cell schema for BASS admission.
        # ne_eff is the cell time-average represented by this solver's quadrature.
        # This projection is not an independent accuracy test or native BASS receipt.
        dt=np.diff(h['t_s']);dtau=np.diff(h['tau'])
        ne_eff_m3=dtau/(C_CM_S*SIGMA_T_CM2*dt)*1e6
        cellfile=root/f'{name}_BASS_CELLS.csv'
        np.savetxt(cellfile,np.column_stack([h['t_s'][:-1],h['t_s'][1:],h['z'][:-1],h['z'][1:],ne_eff_m3,dtau]),
                   delimiter=',',header='t0_s,t1_s,mean_z0,mean_z1,ne_eff_m3,delta_tau',comments='',fmt='%.16e')
        outputs.append({'file':cellfile.name,'sha256':sha(cellfile),'cells':len(dt),
            'meaning':'new reduced-model proper-time cells, ne averaged by producer quadrature',
            'native_BASS_adoption':'NOT_EXECUTED','observer_tail':'ABSENT','tilt':0})
    out={'status':'PASS' if all(x['pass'] for x in results) else 'FAIL','results':results,
        'BASS_exports':outputs,'source_hashes':{n:sha(HERE/n) for n in ['model.py','reference.py','validate_campaign.py']}}
    (root/'INDEPENDENT_COMPARISON.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'metrics':[x['comparison'] for x in results]},indent=2))
    if out['status']!='PASS':raise RuntimeError('INDEPENDENT_REFERENCE_FAILURE')

if __name__=='__main__':main()
