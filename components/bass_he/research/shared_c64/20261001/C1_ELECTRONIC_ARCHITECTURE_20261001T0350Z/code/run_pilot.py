"""Bounded C1 single-R pilot; JSONL survives failures. No asymptotic R grid."""
from pathlib import Path
import json,time,sys,platform,hashlib,os,tempfile
import numpy as np
import scipy
import spheroidal as sp
import partialwave as pw
from coupling import direct,torque,invariants

ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'evidence/PILOT_EVENTS.jsonl'
OUT=ROOT/'evidence/C1_SINGLE_POINT_PILOT.json'
start=time.perf_counter()
records=[]
def event(x):
    x={'elapsed_seconds':time.perf_counter()-start,**x}
    with LOG.open('a') as f:
        f.write(json.dumps(x,allow_nan=False)+'\n'); f.flush(); os.fsync(f.fileno())
    print(json.dumps(x,allow_nan=False),flush=True)
    records.append(x)
def preflight():
    if LOG.exists() or OUT.exists(): raise FileExistsError('create-only pilot outputs already exist')

def atomic_new_json(path,data):
    payload=(json.dumps(data,indent=2,allow_nan=False)+'\n').encode()
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(payload); f.flush(); os.fsync(f.fileno())
        os.link(tmp,path)  # atomic create-only publication, never overwrite
        dfd=os.open(path.parent,os.O_DIRECTORY)
        try: os.fsync(dfd)
        finally: os.close(dfd)
    finally:
        os.unlink(tmp)

def run():
    event({'event':'START','R':2,'charges':[1,2],'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,
           'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')},
           'contract_sha256':hashlib.sha256((ROOT/'NUMERICAL_CONTRACT.json').read_bytes()).hexdigest()})
    sph=[]; ref=[]
    for tag,cfg in [('base',sp.SpheroidalConfig()),('refined',sp.SpheroidalConfig(radial_elements=48,angular_elements=20,radial_extent=30))]:
        g=sp.solve(2,m=0,config=cfg); b=sp.solve(2,m=1,config=cfg)
        d=direct(g,b,12); t=torque(g,b,16); tq=torque(g,b,24)
        x={'event':'SPHEROIDAL','tag':tag,'g':g.metadata(),'b':b.metadata(),'direct':d,'torque':tq,
           'invariants':invariants(g,b,d,tq),'force_q16_to_q24_abs':abs(t['L_O_bar']-tq['L_O_bar'])}
        sph.append(x);event(x)
    for lmax,el,rmax in [(8,40,20),(12,56,24),(18,56,24)]:
        if time.perf_counter()-start>180: raise TimeoutError('bounded pilot budget exhausted')
        g=pw.solve(2,m=0,lmax=lmax,elements=el,rmax=rmax)
        b=pw.solve(2,m=1,lmax=lmax,elements=el,rmax=rmax)
        l=pw.direct_angular_coupling(g,b)
        x={'event':'PARTIALWAVE','lmax':lmax,'energies':[g.energy,b.energy],'direct_L_O_bar':l,
           'residuals':[g.residual,b.residual],'norms':[g.mass_norm,b.mass_norm],
           'metadata':[g.metadata,b.metadata]}
        ref.append(x);event(x)
    target=sph[-1]
    comparison={'energy_abs':[abs(ref[-1]['energies'][i]-target[k]['energy']) for i,k in enumerate(('g','b'))],
       'direct_abs':abs(ref[-1]['direct_L_O_bar']-target['direct']['L_O_bar']),
       'spheroidal_energy_refinement_abs':[abs(sph[0][k]['energy']-sph[1][k]['energy']) for k in ('g','b')],
       'spheroidal_direct_refinement_abs':abs(sph[0]['direct']['L_O_bar']-sph[1]['direct']['L_O_bar']),
       'reference_l12_to_l18_direct_abs':abs(ref[-1]['direct_L_O_bar']-ref[-2]['direct_L_O_bar'])}
    event({'event':'COMPARISON',**comparison})
    atomic_new_json(OUT,{'scope':'C1 only; R=2 a_A; no continuum certificate','spheroidal':sph,'reference':ref,'comparison':comparison,'elapsed_seconds':time.perf_counter()-start})
    event({'event':'COMPLETE','output':str(OUT),'result_sha256':hashlib.sha256(OUT.read_bytes()).hexdigest()})
if __name__=='__main__':
    preflight()  # outside failure logger: preserve already-existing evidence
    try:run()
    except Exception as exc:
        event({'event':'FAILED','type':type(exc).__name__,'message':str(exc)})
        raise
