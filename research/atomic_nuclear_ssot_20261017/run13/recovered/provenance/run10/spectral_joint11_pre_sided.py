"""RUN11 same inherited RHS; scalar root evaluation and event-boundary checkpoints.
No state/source compression other than inherited exact +/-mu reflection. A chunk
ends only at a predeclared event. Restart reuses the same local ODE subproblems.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,time,pathlib,hashlib,argparse,traceback
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from retarded_integrator import RetardedModel,coalesce_reflections,GasServer
R=pathlib.Path(__file__).resolve().parents[1]
class SpectralModel(RetardedModel):
    def scalar_energy(self,z,j):
        a,b,_,_=self.geometry(z);co=self.coh[j];u=self.mu2[j]
        return self.eb[j]*np.sqrt((co[2]/a)**2*((1-u)*np.exp(2*(b-co[3]))+u*np.exp(-4*(b-co[3]))))
    def prepare_events(self):
        end=self.rays(1.,self.m)[0];edges=np.maximum(self.chi,[13.6,24.59,54.42,13.6]);roots=[]
        for sp,edge in enumerate(edges):
            for j in np.flatnonzero((self.eb>edge)&(end<edge)):
                z=brentq(lambda z:self.scalar_energy(z,j)-edge,float(self.birth[j]),1.,xtol=2e-13,rtol=4*np.finfo(float).eps)
                roots.append([float(z),int(j),int(sp),float(self.scalar_energy(z,j)-edge)])
        points=np.unique(np.r_[0.,1.,self.birth,[q[0] for q in roots]])
        return dict(points=points.tolist(),roots=roots,max_energy_residual_eV=max([abs(q[3]) for q in roots],default=0.))

def prepare(m):
    f=R/f'inputs/spectral11/m{m}.json';packet=json.loads(f.read_text());model=SpectralModel(coalesce_reflections(packet));t=time.perf_counter();e=model.prepare_events()
    e.update(packet_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),physical_cohorts=len(packet['cohorts']),dimension=model.dim,event_preparation_wall_s=time.perf_counter()-t)
    p=R/f'inputs/spectral11/m{m}_events.json';p.write_text(json.dumps(e)+'\n');return e

def chunk(m,rtol=3e-11,budget=20.):
    f=R/f'inputs/spectral11/m{m}.json';key=f'm{m}_{rtol:.0e}';out=R/'evidence'/f'joint11_{key}';out.mkdir(exist_ok=True)
    packet=json.loads(f.read_text());model=SpectralModel(coalesce_reflections(packet));ed=json.loads((R/f'inputs/spectral11/m{m}_events.json').read_text());points=ed['points']
    ident=hashlib.sha256(f.read_bytes()).hexdigest();assert ed['packet_sha256']==ident
    saved=out/'checkpoint.npz';meta=out/'checkpoint.json'
    if saved.exists():
        rec=json.loads(meta.read_text());assert rec['packet_sha256']==ident and rec['rtol']==rtol
        y=np.load(saved)['state'];i=rec['next_segment']
    else:
        y=model.y0.copy();i=0;rec=dict(packet_sha256=ident,rtol=rtol,next_segment=0,segments=[],chunk_wall_s=[],status='IN_PROGRESS')
    if rec['status']=='COMPLETE':print(key,'already COMPLETE');return
    atol=np.full(model.dim,1e-13);atol[:13]=1e-17;atol[14:27]=1e-20;atol[27:model.p]=1e-11;atol[model.p:]=1e-19
    factor=np.sqrt(model.dim);atol/=factor
    start=time.perf_counter();begin=i
    with GasServer() as server:
        model.server=server
        while i<len(points)-1:
            left,right=points[i:i+2];active=int(np.searchsorted(model.birth,left,side='right'))
            sol=solve_ivp(lambda z,s:model.raw_rhs(z,s,active),(left,right),y,method='DOP853',rtol=rtol/factor,atol=atol,max_step=.02)
            if not sol.success or sol.t[-1]!=right:raise RuntimeError(sol.message)
            if (sol.y[:13]<0).any() or (sol.y[13]<=0).any():raise ValueError('negative accepted gas')
            if active and sol.y[27:27+active].min() < -1e-12:raise ValueError('negative accepted depth')
            y=sol.y[:,-1].copy();rec['segments'].append([left,right,active,int(sol.nfev),len(sol.t)])
            i+=1
            if time.perf_counter()-start>=budget:break
    model.server=None
    rec['next_segment']=i;rec['chunk_wall_s'].append(time.perf_counter()-start)
    if i==len(points)-1:
        rec.update(status='COMPLETE',observable=model.observables(y),dimension=model.dim,physical_cohorts=len(packet['cohorts']),threshold_roots=len(ed['roots']),birth_times=len(np.unique(model.birth)))
        np.savez_compressed(out/'endpoint.npz',state=y)
    np.savez_compressed(saved,state=y);meta.write_text(json.dumps(rec)+'\n')
    if rec['status']=='COMPLETE':(out/'result.json').write_text(json.dumps(rec,indent=2)+'\n')
    print(json.dumps(dict(key=key,status=rec['status'],segments=[begin,i,len(points)-1],chunk_wall=rec['chunk_wall_s'][-1],total_wall=sum(rec['chunk_wall_s']),observable=rec.get('observable'))))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['prepare','chunk']);ap.add_argument('m',type=int);ap.add_argument('--rtol',type=float,default=3e-11);ap.add_argument('--budget',type=float,default=20.);a=ap.parse_args()
    if a.action=='prepare':
        e=prepare(a.m);print({k:v for k,v in e.items() if k not in ('points','roots')},'points',len(e['points']),'roots',len(e['roots']))
    else:chunk(a.m,a.rtol,a.budget)
