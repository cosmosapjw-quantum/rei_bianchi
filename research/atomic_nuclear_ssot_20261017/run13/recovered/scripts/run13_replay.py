"""Selective RUN13 restart check. Replays a stored tail, NOT the full IVP."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import hashlib,json,pathlib,time
import numpy as np
from scipy.integrate import solve_ivp
from spectral_joint11 import SpectralModel,coalesce_reflections,GasServer
R=pathlib.Path(__file__).resolve().parents[1]

def replay():
    start=time.perf_counter();meta=json.loads((R/'evidence/run13/REPLAY_SEED.json').read_text())
    packet=R/'inputs/spectral11/m2.json';events=R/'inputs/spectral11/m2_events.json';seed=R/meta['state_path']
    for p,h in ((packet,meta['packet_sha256']),(events,meta['events_sha256']),(seed,meta['state_sha256'])):
        if hashlib.sha256(p.read_bytes()).hexdigest()!=h:raise ValueError('replay input hash mismatch')
    model=SpectralModel(coalesce_reflections(json.loads(packet.read_text())));points=json.loads(events.read_text())['points']
    with np.load(seed,allow_pickle=False) as data:y=data['state'].copy()
    atol=np.full(model.dim,1e-13);atol[:13]=1e-17;atol[14:27]=1e-20;atol[27:model.p]=1e-11;atol[model.p:]=1e-19
    factor=np.sqrt(model.dim);atol/=factor
    with GasServer() as server:
        model.server=server
        for i in range(meta['start_segment'],len(points)-1):
            left,right=points[i:i+2];active=int(np.searchsorted(model.birth,left,side='right'));model.set_interval(left,right,active)
            sol=solve_ivp(lambda z,s:model.section_rhs(z,s,active),(left,right),y,method='DOP853',rtol=meta['rtol']/factor,atol=atol,max_step=.02)
            if not sol.success or sol.t[-1]!=right:raise RuntimeError(sol.message)
            if np.any(sol.y[:13]<0) or np.any(sol.y[13]<=0):raise ValueError('negative accepted state')
            y=sol.y[:,-1].copy()
    model.server=None
    with np.load(R/meta['endpoint_path'],allow_pickle=False) as data:expected=data['state'].copy()
    if not np.array_equal(y,expected):raise ValueError('tail endpoint differs')
    result={'scope':'SAVED_EVENT_TAIL_ONLY_NOT_FULL_IVP','start_segment':meta['start_segment'],'end_segment':len(points)-1,'dimension':model.dim,'state_float64_exact_equal':True,'wall_s':time.perf_counter()-start,'observable':model.observables(y)}
    print(json.dumps(result));return result
if __name__=='__main__':replay()
