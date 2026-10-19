"""Selective verification: fresh m0 baseline or saved refined tail, never a full sweep."""
import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'): os.environ[key]='1'
import argparse, hashlib, json, pathlib, time
import numpy as np
from scipy.integrate import solve_ivp
from spectral_joint11 import SpectralModel, coalesce_reflections, GasServer, R
from retarded_integrator import solve_packet

def replay(mode):
    started=time.perf_counter()
    if mode=='baseline':
        packet=json.loads((R/'inputs/spectral11/m0.json').read_text())
        model=SpectralModel(coalesce_reflections(packet))
        y,record=solve_packet(model,rtol=3e-11,wall_cap=30.)
        endpoint=R/'evidence/joint11_m0_3e-11/endpoint.npz'
        scope='fresh initial-state m0 full interval; not refined m1'
    else:
        seed=R/'evidence/replay_seed';meta=json.loads((seed/'receipt.json').read_text())
        p=R/'inputs/spectral11/m1.json';s=seed/'state_3012.npz'
        assert hashlib.sha256(p.read_bytes()).hexdigest()==meta['packet_sha256']
        assert hashlib.sha256(s.read_bytes()).hexdigest()==meta['state_sha256']
        model=SpectralModel(coalesce_reflections(json.loads(p.read_text())))
        with np.load(s) as z:y=z['state'].copy()
        points=json.loads((R/'inputs/spectral11/m1_events.json').read_text())['points']
        tol=np.full(model.dim,1e-13);tol[:13]=1e-17;tol[14:27]=1e-20;tol[27:model.p]=1e-11;tol[model.p:]=1e-19
        factor=np.sqrt(model.dim);tol/=factor;calls=0
        with GasServer() as server:
            model.server=server
            for i in range(meta['start_segment'],len(points)-1):
                left,right=points[i:i+2];active=int(np.searchsorted(model.birth,left,side='right'))
                model.set_interval(left,right,active)
                sol=solve_ivp(lambda t,state:model.section_rhs(t,state,active),(left,right),y,method='DOP853',rtol=meta['rtol']/factor,atol=tol,max_step=.02)
                assert sol.success and sol.t[-1]==right
                assert np.all(sol.y[:13]>=0) and np.all(sol.y[13]>0)
                y=sol.y[:,-1].copy();calls+=sol.nfev
        model.server=None
        record={'replayed_segments':len(points)-1-meta['start_segment'],'nfev':calls,'rtol':meta['rtol']}
        endpoint=R/'evidence/joint11_sided_m1_6e-12/endpoint.npz'
        scope='stored intermediate state segment3012 to3200 only; NOT full m1 trajectory from IC'
    with np.load(endpoint) as f:expected=f['state'].copy()
    assert np.array_equal(y,expected),'deterministic endpoint mismatch'
    result=dict(scope=scope,endpoint_float64_exact_equal=True,dimension=len(y),wall_s=time.perf_counter()-started,observable=model.observables(y))
    print(json.dumps(result));return result
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('mode',choices=['baseline','tail']);replay(a.parse_args().mode)
